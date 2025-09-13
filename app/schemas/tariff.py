from pydantic import BaseModel
from datetime import date
from typing import Optional


class TariffBase(BaseModel):
    start_date: date
    end_date: date
    purchase_low_eur_kwh: float
    purchase_high_eur_kwh: float
    sale_eur_kwh: float
    vat: float
    fixed_roi_rate: Optional[float] = None


class TariffCreate(TariffBase):
    pass


class TariffUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    purchase_low_eur_kwh: Optional[float] = None
    purchase_high_eur_kwh: Optional[float] = None
    sale_eur_kwh: Optional[float] = None
    vat: Optional[float] = None
    fixed_roi_rate: Optional[float] = None


class Tariff(TariffBase):
    id: int

    class Config:
        from_attributes = True
