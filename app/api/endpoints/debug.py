import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import Base
from app.models import models

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/debug/clear-database", status_code=204)
def clear_database(
    db: Session = Depends(deps.get_db)
):
    """
    Clear all data from the database.
    """
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        logger.info("Database cleared successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

from app.crud import crud_debug

@router.post("/debug/fill-database", status_code=200)
def fill_database(
    db: Session = Depends(deps.get_db)
):
    """
    Fill the database with mockup data for 2.5 years.
    """
    try:
        crud_debug.fill_database_with_mock_data(db)
        logger.info("Database filled with mock data successfully.")
        return {"message": "Database filled with mock data successfully."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error filling database with mock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
