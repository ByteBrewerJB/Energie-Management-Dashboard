"""Pydantic schemas for battery resources."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BatteryBase(BaseModel):
    """Shared properties for battery resources."""

    name: Optional[str] = None
    brand: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[Decimal] = None
    capacity_kwh: Optional[float] = None


class BatteryCreate(BatteryBase):
    """Properties required to create a battery."""

    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    capacity_kwh: float


class BatteryUpdate(BatteryBase):
    """Properties that can be updated for a battery."""

    pass


class BatteryInDBBase(BatteryBase):
    """Base properties stored in the database."""

    id: int
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    capacity_kwh: float

    model_config = ConfigDict(from_attributes=True)


class Battery(BatteryInDBBase):
    """Properties returned to the API client."""

    pass
