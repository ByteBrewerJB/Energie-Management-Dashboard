import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.models import models

# Use a separate test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

from datetime import date

def test_clear_database(db_session):
    # Add some data to the database
    solar_panel = models.SolarPanel(
        purchase_date=date(2022, 1, 1),
        purchase_cost_eur=5000,
        total_power_wp=3000,
    )
    db_session.add(solar_panel)
    db_session.commit()

    # Check that the data is there
    assert db_session.query(models.SolarPanel).count() == 1

    # Call the clear-database endpoint
    response = client.post("/api/debug/clear-database")
    assert response.status_code == 204

    # Check that the data is gone
    assert db_session.query(models.SolarPanel).count() == 0

def test_fill_database(db_session):
    # Call the fill-database endpoint
    response = client.post("/api/debug/fill-database")
    assert response.status_code == 200
    assert response.json() == {"message": "Database filled with mock data successfully."}

    # Check that the data is there
    assert db_session.query(models.SolarPanel).count() == 1
    assert db_session.query(models.Battery).count() == 1
    assert db_session.query(models.Car).count() == 1
    assert db_session.query(models.Tariff).count() == 3
    assert db_session.query(models.MonthlyJournal).count() == 30
    assert db_session.query(models.CarJournalEntry).count() == 30
