import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_debug
from app.db.session import Base, get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/clear-database", status_code=status.HTTP_204_NO_CONTENT)
def clear_database(
    db: Session = Depends(get_db),
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

@router.post("/fill-database", status_code=status.HTTP_200_OK)
def fill_database(
    db: Session = Depends(get_db),
):
    """
    Fill the database with mockup data for 2 years.
    """
    try:
        crud_debug.fill_database_with_mock_data(db)
        logger.info("Database filled with mock data successfully.")
        return {"message": "Database filled with mock data successfully."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error filling database with mock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
