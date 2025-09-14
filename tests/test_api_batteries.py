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
def test_create_battery(db_session):
    response = client.post("/api/batteries/", json={"name": "Test Battery", "purchase_date": "2023-01-01", "purchase_cost_eur": 3000, "capacity_kwh": 10.0, "brand": "TestBrand"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Battery"
    assert data["brand"] == "TestBrand"

def test_create_battery_without_brand(db_session):
    response = client.post("/api/batteries/", json={"name": "Test Battery No Brand", "purchase_date": "2023-01-01", "purchase_cost_eur": 3000, "capacity_kwh": 10.0})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Battery No Brand"
    assert data["brand"] is None

def test_read_batteries(db_session):
    client.post("/api/batteries/", json={"name": "Test Battery 1", "purchase_date": "2023-01-01", "purchase_cost_eur": 3000, "capacity_kwh": 10.0})
    client.post("/api/batteries/", json={"name": "Test Battery 2", "purchase_date": "2023-01-02", "purchase_cost_eur": 3500, "capacity_kwh": 12.0})
    response = client.get("/api/batteries/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_update_battery(db_session):
    response = client.post("/api/batteries/", json={"name": "Original Battery", "purchase_date": "2023-01-01", "purchase_cost_eur": 3000, "capacity_kwh": 10.0})
    battery_id = response.json()["id"]
    response = client.put(f"/api/batteries/{battery_id}", json={"name": "Updated Battery"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Battery"

def test_delete_battery(db_session):
    response = client.post("/api/batteries/", json={"name": "To Be Deleted", "purchase_date": "2023-01-01", "purchase_cost_eur": 3000, "capacity_kwh": 10.0})
    battery_id = response.json()["id"]
    response = client.delete(f"/api/batteries/{battery_id}")
    assert response.status_code == 200
    response = client.get(f"/api/batteries/{battery_id}")
    assert response.status_code == 404
