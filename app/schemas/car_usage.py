from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal


# Shared properties
class CarUsageBase(BaseModel):
    car_id: Optional[int] = None
    period_start: Optional[date] = None
    total_charged_kwh: Optional[float] = None
    reimbursement_rate_eur_per_kwh: Optional[Decimal] = None


# Properties to receive on item creation
class CarUsageCreate(CarUsageBase):
    car_id: int
    period_start: date
    total_charged_kwh: float
    reimbursement_rate_eur_per_kwh: Decimal


# Properties to receive on item update
class CarUsageUpdate(CarUsageBase):
    pass


# Properties shared by models stored in DB
class CarUsageInDBBase(CarUsageBase):
    id: int
    car_id: int
    period_start: date
    total_charged_kwh: float
    reimbursement_rate_eur_per_kwh: Decimal

    class Config:
        orm_mode = True


# Properties to return to client
class CarUsage(CarUsageInDBBase):
    pass
