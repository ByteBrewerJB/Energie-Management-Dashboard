from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal


# Shared properties
class BatteryBase(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[Decimal] = None
    capacity_kwh: Optional[float] = None


# Properties to receive on item creation
class BatteryCreate(BatteryBase):
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    capacity_kwh: float


# Properties to receive on item update
class BatteryUpdate(BatteryBase):
    pass


# Properties shared by models stored in DB
class BatteryInDBBase(BatteryBase):
    id: int
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    capacity_kwh: float

    class Config:
        orm_mode = True


# Properties to return to client
class Battery(BatteryInDBBase):
    pass
