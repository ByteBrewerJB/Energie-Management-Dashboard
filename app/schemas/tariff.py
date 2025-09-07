from pydantic import BaseModel
from datetime import date
from typing import Optional


# Shared properties
class TariffBase(BaseModel):
    """Base schema for tariffs, containing all shared properties."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    purchase_low_eur_kwh: Optional[float] = None
    purchase_high_eur_kwh: Optional[float] = None
    sale_eur_kwh: Optional[float] = None
    vat_percentage: Optional[float] = None
    fixed_roi_rate_eur_kwh: Optional[float] = None


# Properties to receive on item creation
class TariffCreate(TariffBase):
    """Schema for creating a new tariff, with required fields."""
    start_date: date
    purchase_low_eur_kwh: float
    purchase_high_eur_kwh: float
    sale_eur_kwh: float
    vat_percentage: float


# Properties to receive on item update
class TariffUpdate(TariffBase):
    """Schema for updating an existing tariff. All fields are optional."""
    pass


# Properties shared by models stored in DB
class TariffInDBBase(TariffBase):
    """Base schema for tariffs as stored in the database."""
    id: int
    start_date: date
    purchase_low_eur_kwh: float
    purchase_high_eur_kwh: float
    sale_eur_kwh: float
    vat_percentage: float

    class Config:
        orm_mode = True


# Properties to return to client
class Tariff(TariffInDBBase):
    """Schema for returning tariff data to the client."""
    pass
