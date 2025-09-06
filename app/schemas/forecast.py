from pydantic import BaseModel
from typing import List, Dict

class MonthlyAverage(BaseModel):
    month: int
    average_production: float

class Forecast(BaseModel):
    month: int
    year: int
    predicted_production: float

class ForecastResult(BaseModel):
    historical_averages: List[MonthlyAverage]
    forecast: List[Forecast]
