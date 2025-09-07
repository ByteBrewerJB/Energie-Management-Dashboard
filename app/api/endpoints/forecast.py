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

    This endpoint generates a forecast by calculating the average production
    for each month from historical records and projecting it for the next 12
    months.

    Args:
        db: The database session dependency.

    Returns:
        A ForecastResult object containing historical monthly averages and the
        12-month forecast.
    """
    return forecasting.get_production_forecast(db)
