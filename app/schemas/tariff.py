"""Pydantic schemas for tariff resources."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

# --- Base Properties ---
class TariffBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    purchase_low_eur_kwh: Decimal
    purchase_high_eur_kwh: Decimal
    sale_eur_kwh: Decimal
    vat_percentage: Decimal
    fixed_roi_rate_eur_kwh: Optional[Decimal] = None

# --- Properties to receive on creation ---
class TariffCreate(TariffBase):
    pass

# --- Properties to receive on update ---
class TariffUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    purchase_low_eur_kwh: Optional[Decimal] = None
    purchase_high_eur_kwh: Optional[Decimal] = None
    sale_eur_kwh: Optional[Decimal] = None
    vat_percentage: Optional[Decimal] = None
    fixed_roi_rate_eur_kwh: Optional[Decimal] = None

# --- Properties shared by models stored in DB ---
class TariffInDBBase(TariffBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Properties to return to client ---
class Tariff(TariffInDBBase):
    pass

# --- Properties stored in DB ---
class TariffInDB(TariffInDBBase):
    pass
