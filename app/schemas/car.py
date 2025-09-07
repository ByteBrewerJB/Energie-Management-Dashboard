from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List

# Forward reference for CarUsage will be handled by Pydantic
# thanks to `from __future__ import annotations`
from .car_usage import CarUsage


# Shared properties
class CarBase(BaseModel):
    name: Optional[str] = None


# Properties to receive on item creation
class CarCreate(CarBase):
    name: str


# Properties to receive on item update
class CarUpdate(CarBase):
    pass


# Properties shared by models stored in DB
class CarInDBBase(CarBase):
    id: int
    name: str

    class Config:
        # Pydantic v2 uses `from_attributes` instead of `orm_mode`
        from_attributes = True


# Properties to return to client
class Car(CarInDBBase):
    pass

# This is for relating the car usage records when fetching a car
class CarWithUsage(Car):
    usage_records: List['CarUsage'] = []
