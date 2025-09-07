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
def test_create_investment(db_session):
    """
    Test creating an investment.
    """
    response = client.post(
        "/api/investments",
        json={
            "name": "My Solar Panels",
            "purchase_date": "2023-01-01",
            "purchase_cost_eur": 10000,
            "total_power_wp": 4000,
            "expected_annual_yield_kwh": 3800,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Solar Panels"
    assert data["id"] is not None

def test_read_investments(db_session):
    """
    Test reading multiple investments.
    """
    client.post(
        "/api/investments",
        json={
            "name": "My Solar Panels",
            "purchase_date": "2023-01-01",
            "purchase_cost_eur": 10000,
            "total_power_wp": 4000,
            "expected_annual_yield_kwh": 3800,
        },
    )
    response = client.get("/api/investments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "My Solar Panels"

def test_read_investment(db_session):
    """
    Test reading a single investment.
    """
    post_response = client.post(
        "/api/investments",
        json={
            "name": "My Solar Panels",
            "purchase_date": "2023-01-01",
            "purchase_cost_eur": 10000,
            "total_power_wp": 4000,
            "expected_annual_yield_kwh": 3800,
        },
    )
    investment_id = post_response.json()["id"]
    response = client.get(f"/api/investments/{investment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Solar Panels"

def test_update_investment(db_session):
    """
    Test updating an investment.
    """
    post_response = client.post(
        "/api/investments",
        json={
            "name": "My Solar Panels",
            "purchase_date": "2023-01-01",
            "purchase_cost_eur": 10000,
            "total_power_wp": 4000,
            "expected_annual_yield_kwh": 3800,
        },
    )
    investment_id = post_response.json()["id"]
    response = client.put(
        f"/api/investments/{investment_id}",
        json={"name": "New Solar Panels"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Solar Panels"

def test_delete_investment(db_session):
    """
    Test deleting an investment.
    """
    post_response = client.post(
        "/api/investments",
        json={
            "name": "My Solar Panels",
            "purchase_date": "2023-01-01",
            "purchase_cost_eur": 10000,
            "total_power_wp": 4000,
            "expected_annual_yield_kwh": 3800,
        },
    )
    investment_id = post_response.json()["id"]
    response = client.delete(f"/api/investments/{investment_id}")
    assert response.status_code == 200
    get_response = client.get(f"/api/investments/{investment_id}")
    assert get_response.status_code == 404
