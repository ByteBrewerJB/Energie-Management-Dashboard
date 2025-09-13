from pydantic import BaseModel
from typing import List, Dict


class MonthlyAverage(BaseModel):
    """Schema for historical average production for a specific month."""
    month: int
    average_production: float


class Forecast(BaseModel):
    """Schema for a single month's production forecast."""
    month: int
    year: int
    predicted_production: float


class ForecastResult(BaseModel):
    """Schema for the complete forecast result."""
    historical_averages: List[MonthlyAverage]
    forecast: List[Forecast]
