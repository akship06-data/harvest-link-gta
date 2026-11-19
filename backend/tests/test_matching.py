import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.matching import haversine_km

SQLALCHEMY_TEST_URL = "sqlite:///./test_harvestlink.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_haversine_dundas_to_sherbourne():
    dist = haversine_km(43.6561, -79.3802, 43.6568, -79.3725)
    assert 0.4 <= dist <= 0.9


def test_rejects_short_expiry_food_safety_guardrail():
    donor = client.post(
        "/api/organizations",
        json={
            "name": "TMU Catering",
            "org_type": "donor",
            "neighborhood": "Dundas",
            "address": "55 Gould St",
            "latitude": 43.6577,
            "longitude": -79.3788,
            "dinesafe_verified": True,
        },
    ).json()

    res = client.post(
        "/api/batches",
        json={
            "donor_id": donor["id"],
            "title": "Perishable Dairy Trays",
            "meal_count": 20,
            "storage_type": "refrigerated",
            "dietary_tags": ["vegetarian"],
            "expires_in_hours": 1.0,
            "sealed_commercial_source": True,
        },
    )
    assert res.status_code == 422


def test_cold_chain_and_dietary_matching_flow():
    donor = client.post(
        "/api/organizations",
        json={
            "name": "Dundas Cafe",
            "org_type": "donor",
            "neighborhood": "Dundas",
            "address": "275 Victoria St",
            "latitude": 43.6563,
            "longitude": -79.3795,
            "dinesafe_verified": True,
        },
    ).json()

    no_fridge_pantry = client.post(
        "/api/organizations",
        json={
            "name": "Dry Goods Pantry",
            "org_type": "pantry",
            "neighborhood": "Dundas",
            "address": "200 Dundas St E",
            "latitude": 43.6565,
            "longitude": -79.3740,
            "has_refrigeration": False,
            "accepted_dietary": ["vegetarian", "shelf_stable"],
        },
    ).json()

    cold_pantry = client.post(
        "/api/organizations",
        json={
            "name": "Dundas Drop-In Fridge",
            "org_type": "pantry",
            "neighborhood": "Dundas",
            "address": "214 Dundas St E",
            "latitude": 43.6568,
            "longitude": -79.3725,
            "has_refrigeration": True,
            "accepted_dietary": ["vegetarian", "halal"],
        },
    ).json()

    batch = client.post(
        "/api/batches",
        json={
            "donor_id": donor["id"],
            "title": "Chilled Vegetarian Meal Boxes",
            "meal_count": 30,
            "storage_type": "refrigerated",
            "dietary_tags": ["vegetarian", "halal"],
            "expires_in_hours": 5.0,
            "sealed_commercial_source": True,
        },
    ).json()

    matches = client.get(f"/api/batches/{batch['id']}/matches").json()
    assert len(matches) == 1
    assert matches[0]["pantry_id"] == cold_pantry["id"]
    assert matches[0]["pantry_id"] != no_fridge_pantry["id"]

    claimed = client.post(
        f"/api/batches/{batch['id']}/claim",
        json={"pantry_id": cold_pantry["id"], "volunteer_name": "Akshara"},
    ).json()
    assert claimed["status"] == "CLAIMED"

    picked_up = client.post(f"/api/batches/{batch['id']}/advance").json()
    assert picked_up["status"] == "PICKED_UP"

    delivered = client.post(f"/api/batches/{batch['id']}/advance").json()
    assert delivered["status"] == "DELIVERED"
