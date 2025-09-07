import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.api.deps import get_current_user
from app.core.security import create_access_token
from datetime import timedelta

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
def test_get_journals_for_year_creates_entries(db_session):
    """
    Test that GET /api/metrics/{year} creates 12 new, empty entries if they don't exist.
    """
    response = client.get("/api/metrics/2025")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12
    for month_data in data:
        assert month_data["metric"]["year"] == 2025
        assert month_data["metric"]["solar_production_kwh"] is None
        assert month_data["metric"]["id"] is not None
        # Also check that the calculated fields are present
        assert "financials" in month_data
        assert "energy_flow" in month_data

def test_update_journal_entry(db_session):
    """
    Test that a PUT request to /api/metrics/{year}/{month} correctly updates an entry.
    """
    # First, ensure the entries for 2026 are created
    client.get("/api/metrics/2026")

    # Now, update one of them
    update_data = {
        "year": 2026,
        "month": 5,
        "grid_consumption_low_kwh": 150.7,
        "solar_production_kwh": 300.2,
        "monthly_prepayment_eur": 100.0
    }
    response = client.put("/api/metrics/2026/5", json=update_data)
    assert response.status_code == 200
    data = response.json()

    # Verify the returned data
    assert data["year"] == 2026
    assert data["month"] == 5
    assert data["grid_consumption_low_kwh"] == 150.7
    assert data["solar_production_kwh"] == 300.2
    assert data["monthly_prepayment_eur"] == "100.00"
    assert data["grid_consumption_high_kwh"] is None # Ensure other fields are untouched

    # Verify the data is persisted by fetching it again
    response_get = client.get("/api/metrics/2026")
    all_months = response_get.json()
    may_data = next((m["metric"] for m in all_months if m["metric"]["month"] == 5), None)
    assert may_data is not None
    assert may_data["solar_production_kwh"] == 300.2

def test_update_nonexistent_journal_fails(db_session):
    """
    Test that a PUT request to a non-existent journal entry fails with a 404.
    """
    # Note: We do not call GET /api/metrics/2027, so no entries exist for this year.
    response = client.put("/api/metrics/2027/1", json={"year": 2027, "month": 1, "solar_production_kwh": 100})
    assert response.status_code == 404
    assert response.json()["detail"] == "Journal not found for this period."

def test_get_journals_for_year_returns_existing(db_session):
    """
    Test that GET /api/metrics/{year} returns existing data without modifying it.
    """
    # Create and update an entry
    client.get("/api/metrics/2028")
    client.put("/api/metrics/2028/3", json={"year": 2028, "month": 3, "solar_production_kwh": 555.5})

    # Fetch the data for the year again
    response = client.get("/api/metrics/2028")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12

    # Check the updated month
    march_data = next((m["metric"] for m in data if m["metric"]["month"] == 3), None)
    assert march_data is not None
    assert march_data["solar_production_kwh"] == 555.5

    # Check a different month to ensure it's still empty
    april_data = next((m["metric"] for m in data if m["metric"]["month"] == 4), None)
    assert april_data is not None
    assert april_data["solar_production_kwh"] is None
