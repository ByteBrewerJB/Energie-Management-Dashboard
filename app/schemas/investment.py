from pydantic import BaseModel
from datetime import date
from typing import Optional

class InvestmentBase(BaseModel):
    description: str
    installation_date: date
    total_cost_eur: float
    total_power_wp: int
    estimated_annual_production_kwh: Optional[int] = None

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentInDB(InvestmentBase):
    id: int

    class Config:
        orm_mode = True
