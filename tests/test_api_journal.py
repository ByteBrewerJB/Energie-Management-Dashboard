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
from app.models import models

def add_journal_entry(db, year, month, data=None):
    if data is None:
        data = {}
    entry_data = {"year": year, "month": month, **data}
    entry = models.MonthlyJournal(**entry_data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def test_update_journal_entry(db_session):
    """
    Test that a PUT request to /api/metrics/{year}/{month} correctly updates an entry.
    """
    # First, create an entry to update
    add_journal_entry(db_session, 2026, 5)

    # Now, update it
    update_data = {
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
    assert data["monthly_prepayment_eur"] == 100.0
    assert data["grid_consumption_high_kwh"] is None # Ensure other fields are untouched

    # Verify the data is persisted by fetching it again
    response_get = client.get("/api/metrics/2026")
    all_months = response_get.json()
    may_data = next((m for m in all_months if m["month"] == 5), None)
    assert may_data is not None
    assert may_data["solar_production_kwh"] == 300.2

def test_update_nonexistent_journal_fails(db_session):
    """
    Test that a PUT request to a non-existent journal entry fails with a 404.
    """
    response = client.put("/api/metrics/2027/1", json={"solar_production_kwh": 100})
    assert response.status_code == 404
    assert response.json()["detail"] == "Journal not found for this period."

def test_get_journals_for_year_returns_existing(db_session):
    """
    Test that GET /api/metrics/{year} returns existing data without modifying it.
    """
    # Create and update an entry
    add_journal_entry(db_session, 2028, 3, {"solar_production_kwh": 555.5})
    add_journal_entry(db_session, 2028, 4)


    # Fetch the data for the year again
    response = client.get("/api/metrics/2028")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Check the updated month
    march_data = next((m for m in data if m["month"] == 3), None)
    assert march_data is not None
    assert march_data["solar_production_kwh"] == 555.5

    # Check a different month to ensure it's still empty
    april_data = next((m for m in data if m["month"] == 4), None)
    assert april_data is not None
    assert april_data["solar_production_kwh"] is None


def test_get_journals_for_future_year(db_session):
    """
    Test that GET /api/metrics/{year} works for a future year.
    """
    add_journal_entry(db_session, 2024, 1, {"solar_production_kwh": 123.4})
    response = client.get("/api/metrics/2024")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["year"] == 2024
    assert data[0]["month"] == 1
    assert data[0]["solar_production_kwh"] == 123.4

def test_get_years(db_session):
    """
    Test that GET /api/metrics/years returns a list of unique years.
    """
    add_journal_entry(db_session, 2022, 1)
    add_journal_entry(db_session, 2023, 1)
    response = client.get("/api/metrics/years")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == [2023, 2022]
