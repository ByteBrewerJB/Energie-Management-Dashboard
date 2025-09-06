from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from decimal import Decimal

# --- Base Schema ---
class SolarInvestmentBase(BaseModel):
    supplier: str
    panels: int
    panel_type: Optional[str] = None
    total_power_wp: Optional[int] = None
    annual_production_kwh: Optional[float] = None
    inverter: Optional[str] = None
    assumed_energy_price_eur_per_kwh: Optional[Decimal] = Decimal('0.40')
    total_cost_eur: Optional[Decimal] = None

# --- Create Schema ---
class SolarInvestmentCreate(SolarInvestmentBase):
    pass

# --- Update Schema ---
class SolarInvestmentUpdate(SolarInvestmentBase):
    pass

# --- Database Schema ---
class SolarInvestmentInDB(SolarInvestmentBase):
    id: UUID

    class Config:
        from_attributes = True

# --- Read/Response Schema ---
class SolarInvestmentRead(SolarInvestmentInDB):
    # Computed fields
    price_per_panel_eur: Optional[Decimal] = None
    savings_first_year_eur: Optional[Decimal] = None
    payback_years: Optional[Decimal] = None
