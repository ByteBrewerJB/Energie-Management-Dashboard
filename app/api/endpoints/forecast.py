from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.forecast import ForecastResult
from app.services import forecasting

router = APIRouter()

@router.get("/forecast/production", response_model=ForecastResult)
def get_production_forecast(db: Session = Depends(get_db)):
    """
    Retrieves a 12-month production forecast based on historical data.
    """
    return forecasting.get_production_forecast(db)
