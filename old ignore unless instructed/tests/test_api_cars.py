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
def test_create_car(db_session):
    response = client.post("/api/cars/", json={"name": "Test Car", "reimbursement_rate_eur_per_kwh": 0.21})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Car"
    assert data["id"] is not None

def test_read_cars(db_session):
    client.post("/api/cars/", json={"name": "Test Car 1", "reimbursement_rate_eur_per_kwh": 0.21})
    client.post("/api/cars/", json={"name": "Test Car 2", "reimbursement_rate_eur_per_kwh": 0.22})
    response = client.get("/api/cars/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Car 1"

def test_update_car(db_session):
    response = client.post("/api/cars/", json={"name": "Original Name", "reimbursement_rate_eur_per_kwh": 0.21})
    car_id = response.json()["id"]
    response = client.put(f"/api/cars/{car_id}", json={"name": "Updated Name"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"

def test_delete_car(db_session):
    response = client.post("/api/cars/", json={"name": "To Be Deleted", "reimbursement_rate_eur_per_kwh": 0.21})
    car_id = response.json()["id"]
    response = client.delete(f"/api/cars/{car_id}")
    assert response.status_code == 200
    response = client.get(f"/api/cars/{car_id}")
    assert response.status_code == 404
