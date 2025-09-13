from pydantic import BaseModel
from typing import Optional
from datetime import date

class BatteryBase(BaseModel):
    name: str
    brand: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: float
    capacity_kwh: float

class BatteryCreate(BatteryBase):
    pass

class BatteryUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[float] = None
    capacity_kwh: Optional[float] = None

class Battery(BatteryBase):
    id: int

    class Config:
        from_attributes = True
