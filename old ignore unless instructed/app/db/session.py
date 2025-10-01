import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

"""
This module handles the database session creation and management.

It sets up the database engine and session factory based on the DATABASE_URL
environment variable. It also provides a dependency `get_db` for use in
FastAPI routes to inject a database session.
"""

# Load environment variables from .env file, so they are available for the app
load_dotenv()

# Read the database URL from the environment variable, with a fallback for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joulejournal.db")

# For SQLite, we need to add a special connect_args argument
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """
    FastAPI dependency to get a database session.

    This function is a generator that creates a new database session for each
    request and ensures that it is closed after the request is finished.

    Yields:
        A new SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
