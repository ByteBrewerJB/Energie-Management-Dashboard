"""Pydantic schemas for solar panel resources."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SolarPanelBase(BaseModel):
    """Shared properties for solar panel resources."""

    name: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[Decimal] = None
    total_power_wp: Optional[int] = None
    expected_annual_yield_kwh: Optional[int] = None


class SolarPanelCreate(SolarPanelBase):
    """Properties required to create a solar panel installation."""

    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    total_power_wp: int


class SolarPanelUpdate(SolarPanelBase):
    """Properties that can be updated for a solar panel installation."""

    pass


class SolarPanelInDBBase(SolarPanelBase):
    """Base properties stored in the database."""

    id: int
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    total_power_wp: int

    model_config = ConfigDict(from_attributes=True)


class SolarPanel(SolarPanelInDBBase):
    """Properties returned to the API client."""

    pass
