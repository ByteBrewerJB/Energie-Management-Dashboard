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
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

# --- Tests ---
def test_create_solar_panel(db_session):
    response = client.post("/api/solar_panels/", json={"name": "Test Solar", "purchase_date": "2023-01-01", "purchase_cost_eur": 5000, "total_power_wp": 4000})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Solar"

def test_create_solar_panel_fails_if_exists(db_session):
    client.post("/api/solar_panels/", json={"name": "Test Solar", "purchase_date": "2023-01-01", "purchase_cost_eur": 5000, "total_power_wp": 4000})
    response = client.post("/api/solar_panels/", json={"name": "Another Solar", "purchase_date": "2023-02-01", "purchase_cost_eur": 6000, "total_power_wp": 5000})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_read_solar_panels(db_session):
    client.post("/api/solar_panels/", json={"name": "Test Solar", "purchase_date": "2023-01-01", "purchase_cost_eur": 5000, "total_power_wp": 4000})
    response = client.get("/api/solar_panels/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_update_solar_panel(db_session):
    response = client.post("/api/solar_panels/", json={"name": "Original Solar", "purchase_date": "2023-01-01", "purchase_cost_eur": 5000, "total_power_wp": 4000})
    panel_id = response.json()["id"]
    response = client.put(f"/api/solar_panels/{panel_id}", json={"name": "Updated Solar"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Solar"

def test_delete_solar_panel(db_session):
    response = client.post("/api/solar_panels/", json={"name": "To Be Deleted", "purchase_date": "2023-01-01", "purchase_cost_eur": 5000, "total_power_wp": 4000})
    panel_id = response.json()["id"]
    response = client.delete(f"/api/solar_panels/{panel_id}")
    assert response.status_code == 200
    response = client.get(f"/api/solar_panels/{panel_id}")
    assert response.status_code == 404
