import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.api.deps import get_current_user
from datetime import date

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

# --- Tests ---
def test_create_tariff(db_session):
    """
    Test creating a tariff.
    """
    response = client.post(
        "/api/tariffs",
        json={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "purchase_low_eur_kwh": 0.2,
            "purchase_high_eur_kwh": 0.3,
            "sale_eur_kwh": 0.1,
            "vat_percentage": 21,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["start_date"] == "2023-01-01"
    assert data["id"] is not None

def test_read_tariffs(db_session):
    """
    Test reading multiple tariffs.
    """
    client.post(
        "/api/tariffs",
        json={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "purchase_low_eur_kwh": 0.2,
            "purchase_high_eur_kwh": 0.3,
            "sale_eur_kwh": 0.1,
            "vat_percentage": 21,
        },
    )
    response = client.get("/api/tariffs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["start_date"] == "2023-01-01"

def test_read_tariff(db_session):
    """
    Test reading a single tariff.
    """
    post_response = client.post(
        "/api/tariffs",
        json={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "purchase_low_eur_kwh": 0.2,
            "purchase_high_eur_kwh": 0.3,
            "sale_eur_kwh": 0.1,
            "vat_percentage": 21,
        },
    )
    tariff_id = post_response.json()["id"]
    response = client.get(f"/api/tariffs/{tariff_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["start_date"] == "2023-01-01"

def test_update_tariff(db_session):
    """
    Test updating a tariff.
    """
    post_response = client.post(
        "/api/tariffs",
        json={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "purchase_low_eur_kwh": 0.2,
            "purchase_high_eur_kwh": 0.3,
            "sale_eur_kwh": 0.1,
            "vat_percentage": 21,
        },
    )
    tariff_id = post_response.json()["id"]
    response = client.put(
        f"/api/tariffs/{tariff_id}",
        json={"sale_eur_kwh": 0.15},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sale_eur_kwh"] == "0.15000"

def test_delete_tariff(db_session):
    """
    Test deleting a tariff.
    """
    post_response = client.post(
        "/api/tariffs",
        json={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "purchase_low_eur_kwh": 0.2,
            "purchase_high_eur_kwh": 0.3,
            "sale_eur_kwh": 0.1,
            "vat_percentage": 21,
        },
    )
    tariff_id = post_response.json()["id"]
    response = client.delete(f"/api/tariffs/{tariff_id}")
    assert response.status_code == 200
    get_response = client.get(f"/api/tariffs/{tariff_id}")
    assert get_response.status_code == 404
