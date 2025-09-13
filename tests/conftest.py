import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.api.deps import get_db
from app.db.session import Base
# Import all models to ensure they are registered with Base
from app.models import user, tariff, car, entity, journal

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This fixture will be used by tests that need a database session.
# It creates the tables, yields a session, and then drops the tables.
@pytest.fixture()
def db() -> Session:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# This fixture provides a test client with the database dependency overridden.
# It depends on the `db` fixture to ensure the database is set up.
@pytest.fixture()
def client(db: Session) -> TestClient:
    def override_get_db_test():
        try:
            yield db
        finally:
            # This close is important, but the outer fixture will handle the transaction
            pass

    app.dependency_overrides[get_db] = override_get_db_test

    with TestClient(app) as c:
        yield c
