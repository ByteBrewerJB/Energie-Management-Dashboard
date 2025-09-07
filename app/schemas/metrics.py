from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal


# Shared properties
class MonthlyMetricBase(BaseModel):
    period_start: Optional[date] = None
    account_name: Optional[str] = None
    production_total_kwh: Optional[float] = None
    grid_consumption_low_kwh: Optional[float] = None
    grid_consumption_high_kwh: Optional[float] = None
    grid_feed_in_low_kwh: Optional[float] = None
    grid_feed_in_high_kwh: Optional[float] = None
    battery_charge_kwh: Optional[float] = None
    battery_discharge_kwh: Optional[float] = None
    monthly_prepayment_eur: Optional[Decimal] = None


# Properties to receive on item creation
class MonthlyMetricCreate(MonthlyMetricBase):
    period_start: date
    account_name: str
    production_total_kwh: float
    grid_consumption_low_kwh: float
    grid_consumption_high_kwh: float
    grid_feed_in_low_kwh: float
    grid_feed_in_high_kwh: float
    monthly_prepayment_eur: Decimal


# Properties to receive on item update
class MonthlyMetricUpdate(MonthlyMetricBase):
    pass


# Properties shared by models stored in DB
class MonthlyMetricInDBBase(MonthlyMetricBase):
    id: int
    period_start: date
    account_name: str
    production_total_kwh: float
    grid_consumption_low_kwh: float
    grid_consumption_high_kwh: float
    grid_feed_in_low_kwh: float
    grid_feed_in_high_kwh: float
    monthly_prepayment_eur: Decimal

    class Config:
        orm_mode = True


# Properties to return to client
class MonthlyMetric(MonthlyMetricInDBBase):
    pass
