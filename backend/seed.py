from datetime import datetime, timedelta, timezone
from app.database import Base, SessionLocal, engine
from app.models import Organization, SurplusBatch


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Organization).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    orgs = [
        Organization(
            name="TMU Student Campus Catering Surplus",
            org_type="donor",
            neighborhood="Yonge-Dundas / TMU",
            address="55 Gould St, Toronto, ON",
            latitude=43.6577,
            longitude=-79.3788,
            dinesafe_verified=True,
            has_refrigeration=True,
            accepted_dietary="vegetarian,halal,nut_free",
        ),
        Organization(
            name="Victoria St Artisan Bakery & Cafe",
            org_type="donor",
            neighborhood="Dundas Square",
            address="275 Victoria St, Toronto, ON",
            latitude=43.6563,
            longitude=-79.3795,
            dinesafe_verified=True,
            has_refrigeration=True,
            accepted_dietary="vegetarian,nut_free,shelf_stable",
        ),
        Organization(
            name="Gerrard & Church Corner Grocer",
            org_type="donor",
            neighborhood="Garden District",
            address="310 Gerrard St E, Toronto, ON",
            latitude=43.6612,
            longitude=-79.3698,
            dinesafe_verified=True,
            has_refrigeration=True,
            accepted_dietary="vegetarian,halal,shelf_stable",
        ),
        Organization(
            name="Dundas-Sherbourne Community Drop-In Pantry",
            org_type="pantry",
            neighborhood="Downtown East / Dundas",
            address="214 Dundas St E, Toronto, ON",
            latitude=43.6568,
            longitude=-79.3725,
            dinesafe_verified=True,
            has_refrigeration=True,
            accepted_dietary="vegetarian,halal,nut_free,shelf_stable",
        ),
        Organization(
            name="TMSU Good Food Centre",
            org_type="pantry",
            neighborhood="TMU Campus",
            address="55 Gould St (Student Centre), Toronto, ON",
            latitude=43.6579,
            longitude=-79.3785,
            dinesafe_verified=True,
            has_refrigeration=True,
            accepted_dietary="vegetarian,halal,nut_free,shelf_stable",
        ),
        Organization(
            name="Kensington Community Fridge Hub",
            org_type="pantry",
            neighborhood="Kensington Market",
            address="180 Baldwin St, Toronto, ON",
            latitude=43.6548,
            longitude=-79.4005,
            dinesafe_verified=True,
            has_refrigeration=False,
            accepted_dietary="vegetarian,shelf_stable",
        ),
    ]
    db.add_all(orgs)
    db.commit()

    now = datetime.now(timezone.utc)
    batches = [
        SurplusBatch(
            donor_id=1,
            title="Untouched Hackathon Catering Trays (Paneer Wraps & Samosas)",
            meal_count=45,
            storage_type="refrigerated",
            dietary_tags="vegetarian,halal,nut_free",
            expires_at=now + timedelta(hours=6),
            status="AVAILABLE",
            safety_checked=True,
        ),
        SurplusBatch(
            donor_id=2,
            title="End-of-Day Sourdough Loaves & Individually Wrapped Muffins",
            meal_count=32,
            storage_type="shelf_stable",
            dietary_tags="vegetarian,nut_free,shelf_stable",
            expires_at=now + timedelta(hours=24),
            status="AVAILABLE",
            safety_checked=True,
        ),
        SurplusBatch(
            donor_id=3,
            title="Fresh Produce Crates (Apples, Bananas, Baby Carrots)",
            meal_count=60,
            storage_type="shelf_stable",
            dietary_tags="vegetarian,halal,nut_free,shelf_stable",
            expires_at=now + timedelta(hours=36),
            matched_pantry_id=4,
            volunteer_name="Akshara P.",
            status="DELIVERED",
            safety_checked=True,
            claimed_at=now - timedelta(hours=2),
            picked_up_at=now - timedelta(hours=1, minutes=30),
            delivered_at=now - timedelta(hours=1),
        ),
    ]
    db.add_all(batches)
    db.commit()
    db.close()
    print("Seeded HarvestLink GTA with Dundas & Downtown Toronto pilot data.")


if __name__ == "__main__":
    seed()
