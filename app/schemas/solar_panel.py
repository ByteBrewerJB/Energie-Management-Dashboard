from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal


# Shared properties
class SolarPanelBase(BaseModel):
    name: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[Decimal] = None
    total_power_wp: Optional[int] = None
    expected_annual_yield_kwh: Optional[int] = None


# Properties to receive on item creation
class SolarPanelCreate(SolarPanelBase):
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    total_power_wp: int


# Properties to receive on item update
class SolarPanelUpdate(SolarPanelBase):
    pass


# Properties shared by models stored in DB
class SolarPanelInDBBase(SolarPanelBase):
    id: int
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    total_power_wp: int

    class Config:
        orm_mode = True


# Properties to return to client
class SolarPanel(SolarPanelInDBBase):
    pass
