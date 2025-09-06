from pydantic import BaseModel
from datetime import date
from typing import Optional

class TariffBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    purchase_low_eur_kwh: float
    purchase_high_eur_kwh: float
    sale_eur_kwh: float
    vat_percentage: float = 0.21
    fixed_roi_rate_eur_kwh: Optional[float] = None

class TariffCreate(TariffBase):
    pass

class TariffInDB(TariffBase):
    id: int

    class Config:
        orm_mode = True
