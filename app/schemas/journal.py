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
    grid_consumption_low_kwh: float
    grid_consumption_high_kwh: float
    grid_feed_in_low_kwh: float
    grid_feed_in_high_kwh: float
    consumption_price_low_eur_kwh: Decimal
    consumption_price_high_eur_kwh: Decimal
    feed_in_tariff_low_eur_kwh: Decimal
    feed_in_tariff_high_eur_kwh: Decimal
    solar_production_kwh: float
    battery_charge_kwh: Optional[float] = 0.0
    battery_discharge_kwh: Optional[float] = 0.0
    monthly_prepayment_eur: Decimal

class MonthlyJournalCreate(MonthlyJournalBase):
    car_entries: List[CarJournalEntryCreate] = []

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
