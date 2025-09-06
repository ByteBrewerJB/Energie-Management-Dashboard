from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from decimal import Decimal

# --- Base Schema ---
class MonthlyEnergyBase(BaseModel):
    year: int
    month: int
    low_tariff_eur_per_kwh: Optional[Decimal] = None
    high_tariff_eur_per_kwh: Optional[Decimal] = None
    feedin_rate_eur_per_kwh: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = Decimal('0.21')
    ev_kwh: Optional[float] = 0.0
    auto_eur: Optional[Decimal] = Decimal(0)
    pv_backfeed_kwh: Optional[float] = 0.0
    pv_production_kwh: Optional[float] = 0.0
    house_low_kwh: Optional[float] = 0.0
    house_high_kwh: Optional[float] = 0.0
    battery_charge_kwh: Optional[float] = 0.0
    battery_discharge_kwh: Optional[float] = 0.0
    grid_import_without_battery_kwh: Optional[float] = None
    grid_export_without_battery_kwh: Optional[float] = None
    advance_payment_eur: Optional[Decimal] = Decimal(0)
    settlement_to_own_account_eur: Optional[Decimal] = Decimal(0)
    provider_name: Optional[str] = "Awesems"
    note: Optional[str] = None
    billed_kwh: Optional[float] = None
    energy_unit_price_eur: Optional[Decimal] = None

# --- Create Schema ---
class MonthlyEnergyCreate(MonthlyEnergyBase):
    pass

# --- Update Schema ---
class MonthlyEnergyUpdate(MonthlyEnergyBase):
    pass

# --- Database Schema ---
class MonthlyEnergyInDB(MonthlyEnergyBase):
    id: UUID

    class Config:
        from_attributes = True

# --- Read/Response Schema ---
class MonthlyEnergyRead(MonthlyEnergyInDB):
    # Computed fields
    house_kwh_total: Optional[float] = None
    pv_self_consumption_kwh: Optional[float] = None
    pv_revenue_eur: Optional[Decimal] = None
    total_consumption_kwh: Optional[float] = None
    self_consumption_ratio: Optional[float] = None
    pv_coverage_ratio: Optional[float] = None
    auto_effective_eur_per_kwh: Optional[Decimal] = None
    billed_total_excl_vat_eur: Optional[Decimal] = None
    billed_total_incl_vat_eur: Optional[Decimal] = None
    month_name: Optional[str] = None
