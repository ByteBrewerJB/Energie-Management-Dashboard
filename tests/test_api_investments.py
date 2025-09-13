import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.api.deps import get_current_user

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# --- Mock Authentication ---
def override_get_current_user():
    return "testuser"

# Apply overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

# --- Pytest Fixtures ---
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Test Data ---
SOLAR_PANEL_PAYLOAD = {
    "type": "solar_panel",
    "name": "My Solar Panels",
    "purchase_date": "2023-01-01",
    "purchase_cost_eur": "10000.50",
    "total_power_wp": 4000,
    "expected_annual_yield_kwh": 3800,
}

BATTERY_PAYLOAD = {
    "type": "battery",
    "name": "My Battery",
    "purchase_date": "2023-02-15",
    "purchase_cost_eur": "8000.75",
}

# --- Tests ---
def test_create_solar_panel_investment(db_session):
    response = client.post("/api/investments", json=SOLAR_PANEL_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Solar Panels"
    assert data["type"] == "solar_panel"
    assert data["id"] is not None

def test_create_battery_investment(db_session):
    response = client.post("/api/investments", json=BATTERY_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Battery"
    assert data["type"] == "battery"
    assert data["id"] is not None

def test_read_all_investments(db_session):
    client.post("/api/investments", json=SOLAR_PANEL_PAYLOAD)
    client.post("/api/investments", json=BATTERY_PAYLOAD)

    response = client.get("/api/investments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    types = {item['type'] for item in data}
    assert types == {"solar_panel", "battery"}
    names = {item['name'] for item in data}
    assert names == {"My Solar Panels", "My Battery"}

def test_read_single_investment(db_session):
    post_response = client.post("/api/investments", json=SOLAR_PANEL_PAYLOAD)
    item_id = post_response.json()["id"]

    response = client.get(f"/api/investments/solar_panel/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Solar Panels"

def test_update_solar_panel_investment(db_session):
    post_response = client.post("/api/investments", json=SOLAR_PANEL_PAYLOAD)
    item_id = post_response.json()["id"]

    update_payload = {"name": "New Solar Panels Name"}
    response = client.put(f"/api/investments/solar_panel/{item_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Solar Panels Name"

def test_update_battery_investment(db_session):
    post_response = client.post("/api/investments", json=BATTERY_PAYLOAD)
    item_id = post_response.json()["id"]

    update_payload = {"name": "New Battery Name"}
    response = client.put(f"/api/investments/battery/{item_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Battery Name"

def test_delete_investment(db_session):
    post_response = client.post("/api/investments", json=SOLAR_PANEL_PAYLOAD)
    item_id = post_response.json()["id"]

    delete_response = client.delete(f"/api/investments/solar_panel/{item_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/api/investments/solar_panel/{item_id}")
    assert get_response.status_code == 404

def test_read_nonexistent_investment(db_session):
    response = client.get("/api/investments/solar_panel/999")
    assert response.status_code == 404

def test_invalid_investment_type(db_session):
    response = client.post(
        "/api/investments",
        json={
            "type": "toaster",
            "name": "My Toaster",
            "purchase_date": "2023-01-01",
            "purchase_cost_eur": 100,
        }
    )
    # This will fail at the Pydantic validation level before reaching the endpoint logic
    assert response.status_code == 422
