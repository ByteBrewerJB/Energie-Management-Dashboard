from pydantic import BaseModel
from typing import Optional
from datetime import date

class SolarPanelBase(BaseModel):
    name: str
    purchase_date: Optional[date] = None
    purchase_cost_eur: float
    power_capacity_kwp: float
    expected_yield_kwh_per_kwp: Optional[float] = None

class SolarPanelCreate(SolarPanelBase):
    pass

class SolarPanelUpdate(BaseModel):
    name: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[float] = None
    power_capacity_kwp: Optional[float] = None
    expected_yield_kwh_per_kwp: Optional[float] = None

class SolarPanel(SolarPanelBase):
    id: int

    class Config:
        from_attributes = True
