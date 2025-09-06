from pydantic import BaseModel
from datetime import date
from typing import Optional

# Shared properties
class MonthlyMetricBase(BaseModel):
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
    period_start: date
    account_name: str
    production_total_kwh: float
    import_low_kwh: float
    import_high_kwh: float
    export_total_kwh: float
    monthly_prepayment_eur: float

# Properties to receive on item update
class MonthlyMetricUpdate(MonthlyMetricBase):
    pass

# Properties shared by models stored in DB
class MonthlyMetricInDBBase(MonthlyMetricBase):
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
    pass
