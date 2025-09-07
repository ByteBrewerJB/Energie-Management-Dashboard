from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List, Optional

# --- Car Journal Entry Schemas ---

class CarJournalEntryBase(BaseModel):
    car_id: int
    total_charged_kwh: float

class CarJournalEntryCreate(CarJournalEntryBase):
    pass

class CarJournalEntry(CarJournalEntryBase):
    id: int
    journal_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Monthly Journal Schemas ---

class MonthlyJournalBase(BaseModel):
    year: int
    month: int
    grid_consumption_low_kwh: Optional[float] = None
    grid_consumption_high_kwh: Optional[float] = None
    grid_feed_in_low_kwh: Optional[float] = None
    grid_feed_in_high_kwh: Optional[float] = None
    consumption_price_low_eur_kwh: Optional[Decimal] = None
    consumption_price_high_eur_kwh: Optional[Decimal] = None
    feed_in_tariff_low_eur_kwh: Optional[Decimal] = None
    feed_in_tariff_high_eur_kwh: Optional[Decimal] = None
    solar_production_kwh: Optional[float] = None
    battery_charge_kwh: Optional[float] = None
    battery_discharge_kwh: Optional[float] = None
    monthly_prepayment_eur: Optional[Decimal] = None

class MonthlyJournalCreate(MonthlyJournalBase):
    car_entries: List[CarJournalEntryCreate] = []


class MonthlyJournalUpdate(BaseModel):
    grid_consumption_low_kwh: Optional[float] = None
    grid_consumption_high_kwh: Optional[float] = None
    grid_feed_in_low_kwh: Optional[float] = None
    grid_feed_in_high_kwh: Optional[float] = None
    consumption_price_low_eur_kwh: Optional[Decimal] = None
    consumption_price_high_eur_kwh: Optional[Decimal] = None
    feed_in_tariff_low_eur_kwh: Optional[Decimal] = None
    feed_in_tariff_high_eur_kwh: Optional[Decimal] = None
    solar_production_kwh: Optional[float] = None
    battery_charge_kwh: Optional[float] = None
    battery_discharge_kwh: Optional[float] = None
    monthly_prepayment_eur: Optional[Decimal] = None


class MonthlyJournal(MonthlyJournalBase):
    id: int
    car_entries: List[CarJournalEntry] = []

    model_config = ConfigDict(from_attributes=True)

# --- Financial Statement Schemas ---

class MonthlyStatement(BaseModel):
    """
    Schema for returning the calculated financial results of a journal entry.
    """
    total_consumption_cost_eur: Decimal
    total_feed_in_revenue_eur: Decimal
    net_energy_cost_eur: Decimal
    total_car_reimbursement_eur: Decimal
    final_settlement_eur: Decimal

# --- Combined Schema for API Response ---

class JournalWithStatement(BaseModel):
    """
    The complete response for a monthly journal, including the raw data
    and the calculated financial statement.
    """
    journal_data: MonthlyJournal
    financial_statement: MonthlyStatement


# --- Frontend-specific Schemas ---

class EnergyFlow(BaseModel):
    """
    Schema for the calculated energy flow metrics required by the frontend.
    """
    self_consumption_kwh: Decimal
    total_household_consumption_kwh: Decimal
    home_consumption_kwh: Decimal
    self_sufficiency_ratio: Decimal
    total_grid_feed_in_kwh: Decimal
    # The frontend expects import_total_kwh, so we need to calculate it.
    # This can be derived from the journal data.
    import_total_kwh: Decimal


class Financials(BaseModel):
    """
    Schema for the calculated financial metrics required by the frontend.
    This is a subset of the full MonthlyStatement.
    """
    net_costs: Decimal


class FrontendChartData(BaseModel):
    """
    The specific nested structure expected by the dashboard frontend.
    """
    metric: MonthlyJournal
    financials: Financials
    energy_flow: EnergyFlow
