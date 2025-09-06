from pydantic import BaseModel
from datetime import date
from typing import Optional

# Shared properties
class InvestmentBase(BaseModel):
    description: Optional[str] = None
    installation_date: Optional[date] = None
    total_cost_eur: Optional[float] = None
    total_power_wp: Optional[int] = None
    estimated_annual_production_kwh: Optional[int] = None

# Properties to receive on item creation
class InvestmentCreate(InvestmentBase):
    description: str
    installation_date: date
    total_cost_eur: float
    total_power_wp: int

# Properties to receive on item update
class InvestmentUpdate(InvestmentBase):
    pass

# Properties shared by models stored in DB
class InvestmentInDBBase(InvestmentBase):
    id: int
    description: str
    installation_date: date
    total_cost_eur: float
    total_power_wp: int

    class Config:
        orm_mode = True

# Properties to return to client
class Investment(InvestmentInDBBase):
    pass
