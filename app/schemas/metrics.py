from pydantic import BaseModel
from datetime import date

class MonthlyMetricBase(BaseModel):
    period: date
    account: str = "household"
    total_generated_kwh: float
    import_low_rate_kwh: float
    import_high_rate_kwh: float
    total_feed_in_kwh: float
    ev_consumption_kwh: float
    battery_charge_kwh: float = 0.0
    battery_discharge_kwh: float = 0.0
    prepayment_amount: float

class MonthlyMetricCreate(MonthlyMetricBase):
    pass

class MonthlyMetricInDB(MonthlyMetricBase):
    id: int

    class Config:
        orm_mode = True
