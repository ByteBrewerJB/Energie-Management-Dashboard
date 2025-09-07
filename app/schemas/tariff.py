from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


# Shared properties
class TariffBase(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    consumption_price_low_eur_kwh: Optional[Decimal] = None
    consumption_price_high_eur_kwh: Optional[Decimal] = None
    feed_in_tariff_low_eur_kwh: Optional[Decimal] = None
    feed_in_tariff_high_eur_kwh: Optional[Decimal] = None
    vat_percentage: Optional[Decimal] = None
    fixed_roi_rate_eur_kwh: Optional[Decimal] = None


# Properties to receive on item creation
class TariffCreate(TariffBase):
    year: int
    month: int
    consumption_price_low_eur_kwh: Decimal
    consumption_price_high_eur_kwh: Decimal
    feed_in_tariff_low_eur_kwh: Decimal
    feed_in_tariff_high_eur_kwh: Decimal
    vat_percentage: Decimal


# Properties to receive on item update
class TariffUpdate(TariffBase):
    pass


# Properties shared by models stored in DB
class TariffInDBBase(TariffBase):
    id: int
    year: int
    month: int
    consumption_price_low_eur_kwh: Decimal
    consumption_price_high_eur_kwh: Decimal
    feed_in_tariff_low_eur_kwh: Decimal
    feed_in_tariff_high_eur_kwh: Decimal
    vat_percentage: Decimal

    class Config:
        orm_mode = True


# Properties to return to client
class Tariff(TariffInDBBase):
    pass
