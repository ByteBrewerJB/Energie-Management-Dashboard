from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# Using newest commit (feat/full-dashboard-refactor): Pydantic v2 style and forward refs via __future__
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

    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class Car(CarInDBBase):
    pass


# Car with related usage records
class CarWithUsage(Car):
    # With __future__ annotations, this will be resolved lazily
    usage_records: List[CarUsage] = []


# Ensure forward refs are resolved (safe no-op if already resolved)
CarWithUsage.model_rebuild()
