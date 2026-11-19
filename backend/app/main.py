from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .matching import rank_pantry_matches
from .models import Organization, SurplusBatch
from .schemas import (
    ClaimRequest,
    OrganizationCreate,
    OrganizationOut,
    PantryMatchOut,
    SurplusBatchCreate,
    SurplusBatchOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HarvestLink GTA API",
    description="Hyper-local food rescue and pantry routing engine for the Dundas & Downtown Toronto corridor.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "corridor": "Dundas / Downtown Toronto"}


@app.get("/api/organizations", response_model=List[OrganizationOut])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()


@app.post("/api/organizations", response_model=OrganizationOut)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    org = Organization(
        name=payload.name,
        org_type=payload.org_type,
        neighborhood=payload.neighborhood,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        dinesafe_verified=payload.dinesafe_verified,
        has_refrigeration=payload.has_refrigeration,
        accepted_dietary=",".join([t.strip().lower() for t in payload.accepted_dietary]),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@app.get("/api/batches", response_model=List[SurplusBatchOut])
def list_batches(db: Session = Depends(get_db)):
    return db.query(SurplusBatch).order_by(SurplusBatch.created_at.desc()).all()


@app.post("/api/batches", response_model=SurplusBatchOut)
def create_batch(payload: SurplusBatchCreate, db: Session = Depends(get_db)):
    donor = db.query(Organization).filter(Organization.id == payload.donor_id, Organization.org_type == "donor").first()
    if not donor:
        raise HTTPException(status_code=404, detail="Verified donor organization not found.")
    if not donor.dinesafe_verified and payload.storage_type != "shelf_stable":
        raise HTTPException(
            status_code=400,
            detail="Unverified donors may only list sealed shelf-stable items.",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    batch = SurplusBatch(
        donor_id=donor.id,
        title=payload.title,
        meal_count=payload.meal_count,
        storage_type=payload.storage_type,
        dietary_tags=",".join([t.strip().lower() for t in payload.dietary_tags]),
        expires_at=expires_at,
        status="AVAILABLE",
        safety_checked=True,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@app.get("/api/batches/{batch_id}/matches", response_model=List[PantryMatchOut])
def get_batch_matches(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(SurplusBatch).filter(SurplusBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Surplus batch not found.")
    donor = db.query(Organization).filter(Organization.id == batch.donor_id).first()
    pantries = db.query(Organization).filter(Organization.org_type == "pantry").all()
    return rank_pantry_matches(batch, donor, pantries)


@app.post("/api/batches/{batch_id}/claim", response_model=SurplusBatchOut)
def claim_batch(batch_id: int, payload: ClaimRequest, db: Session = Depends(get_db)):
    batch = db.query(SurplusBatch).filter(SurplusBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Surplus batch not found.")
    if batch.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail=f"Batch cannot be claimed in status {batch.status}.")

    now = datetime.now(timezone.utc)
    expires = batch.expires_at if batch.expires_at.tzinfo else batch.expires_at.replace(tzinfo=timezone.utc)
    if expires <= now + timedelta(minutes=45):
        raise HTTPException(status_code=400, detail="Batch is too close to food-safety expiration cutoff.")

    pantry = db.query(Organization).filter(Organization.id == payload.pantry_id, Organization.org_type == "pantry").first()
    if not pantry:
        raise HTTPException(status_code=404, detail="Receiving pantry not found.")

    batch.matched_pantry_id = pantry.id
    batch.volunteer_name = payload.volunteer_name.strip()
    batch.status = "CLAIMED"
    batch.claimed_at = now
    db.commit()
    db.refresh(batch)
    return batch


@app.post("/api/batches/{batch_id}/advance", response_model=SurplusBatchOut)
def advance_custody(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(SurplusBatch).filter(SurplusBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Surplus batch not found.")

    now = datetime.now(timezone.utc)
    if batch.status == "CLAIMED":
        batch.status = "PICKED_UP"
        batch.picked_up_at = now
    elif batch.status == "PICKED_UP":
        batch.status = "DELIVERED"
        batch.delivered_at = now
    else:
        raise HTTPException(status_code=400, detail=f"Cannot advance batch from status {batch.status}.")

    db.commit()
    db.refresh(batch)
    return batch
