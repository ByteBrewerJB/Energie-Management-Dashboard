"""Pydantic schemas for car resources."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    """Shared properties for car resources."""

    name: Optional[str] = None
    reimbursement_rate_eur_per_kwh: Optional[Decimal] = None


class CarCreate(CarBase):
    """Properties required to create a car."""

    name: str
    reimbursement_rate_eur_per_kwh: Decimal


class CarUpdate(CarBase):
    """Properties that can be updated for a car."""

    pass


class CarInDBBase(CarBase):
    """Base properties stored in the database."""

    id: int
    name: str
    reimbursement_rate_eur_per_kwh: Decimal

    model_config = ConfigDict(from_attributes=True)


class Car(CarInDBBase):
    """Properties returned to the API client."""

    pass
