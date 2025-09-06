from pydantic import BaseModel
from datetime import date
from typing import Optional


# Shared properties
class MonthlyMetricBase(BaseModel):
    """Base schema for monthly metrics, containing all shared properties."""
    period_start: Optional[date] = None
    account_name: Optional[str] = None
    production_total_kwh: Optional[float] = None
    import_low_kwh: Optional[float] = None
    import_high_kwh: Optional[float] = None
    export_total_kwh: Optional[float] = None
    consumption_ev_kwh: Optional[float] = None
    battery_charge_kwh: Optional[float] = None
    battery_discharge_kwh: Optional[float] = None
    monthly_prepayment_eur: Optional[float] = None


# Properties to receive on item creation
class MonthlyMetricCreate(MonthlyMetricBase):
    """Schema for creating a new monthly metric, with required fields."""
    period_start: date
    account_name: str
    production_total_kwh: float
    import_low_kwh: float
    import_high_kwh: float
    export_total_kwh: float
    monthly_prepayment_eur: float


# Properties to receive on item update
class MonthlyMetricUpdate(MonthlyMetricBase):
    """Schema for updating an existing monthly metric. All fields are optional."""
    pass


# Properties shared by models stored in DB
class MonthlyMetricInDBBase(MonthlyMetricBase):
    """Base schema for monthly metrics as stored in the database."""
    id: int
    period_start: date
    account_name: str
    production_total_kwh: float
    import_low_kwh: float
    import_high_kwh: float
    export_total_kwh: float
    monthly_prepayment_eur: float

    class Config:
        orm_mode = True


# Properties to return to client
class MonthlyMetric(MonthlyMetricInDBBase):
    """Schema for returning monthly metric data to the client."""
    pass
