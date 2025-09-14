import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.api.deps import get_current_user
from app.crud import crud_journal
from app.schemas import journal as journal_schema

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
def test_create_journal_entry(db_session):
    """
    Test that a POST request to /api/journal/ correctly creates an entry.
    """
    payload = {
        "year": 2029,
        "month": 1,
        "solar_production_kwh": 42.0,
        "car_entries": []
    }
    response = client.post("/api/journal/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["year"] == 2029
    assert data["month"] == 1
    assert data["solar_production_kwh"] == 42.0

def test_create_duplicate_journal_entry_fails(db_session):
    """
    Test that creating a journal for a period that already exists fails.
    """
    payload = {"year": 2030, "month": 2, "car_entries": []}
    client.post("/api/journal/", json=payload) # First one is OK
    response = client.post("/api/journal/", json=payload) # Second one should fail
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_get_journals_for_year_returns_empty_list_for_new_year(db_session):
    """
    Test that GET /api/journal/{year} returns an empty list if no entries exist.
    """
    response = client.get("/api/journal/2025")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_get_journal_for_month(db_session):
    """
    Test that GET /api/journal/{year}/{month} returns a single processed entry.
    """
    journal_in = journal_schema.MonthlyJournalCreate(year=2026, month=6, solar_production_kwh=123.4, car_entries=[])
    crud_journal.create_journal(db_session, obj_in=journal_in)
    response = client.get("/api/journal/2026/6")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"]["year"] == 2026
    assert data["metric"]["month"] == 6
    assert data["metric"]["solar_production_kwh"] == 123.4
    assert "financials" in data
    assert "energy_flow" in data

def test_get_nonexistent_journal_for_month_fails(db_session):
    """
    Test that GET for a non-existent month fails with a 404.
    """
    response = client.get("/api/journal/2026/7")
    assert response.status_code == 404

def test_update_journal_entry(db_session):
    """
    Test that a PUT request to /api/journal/{year}/{month} correctly updates an entry.
    """
    journal_in = journal_schema.MonthlyJournalCreate(year=2026, month=5, car_entries=[])
    crud_journal.create_journal(db_session, obj_in=journal_in)
    update_data = {"solar_production_kwh": 300.2}
    response = client.put("/api/journal/2026/5", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["solar_production_kwh"] == 300.2

def test_update_nonexistent_journal_fails(db_session):
    """
    Test that a PUT request to a non-existent journal entry fails with a 404.
    """
    response = client.put("/api/journal/2027/1", json={"solar_production_kwh": 100})
    assert response.status_code == 404
    assert response.json()["detail"] == "Journal not found for this period."
