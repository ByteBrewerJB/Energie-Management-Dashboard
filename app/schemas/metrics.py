from pydantic import BaseModel
from datetime import date

class MonthlyMetricBase(BaseModel):
    period_start: date
    account_name: str
    production_total_kwh: float
    import_low_kwh: float
    import_high_kwh: float
    export_total_kwh: float
    consumption_ev_kwh: float
    battery_charge_kwh: float = 0.0
    battery_discharge_kwh: float = 0.0
    monthly_prepayment_eur: float

class MonthlyMetricCreate(MonthlyMetricBase):
    pass

class MonthlyMetricInDB(MonthlyMetricBase):
    id: int

    class Config:
        orm_mode = True
