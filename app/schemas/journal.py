from pydantic import BaseModel
from typing import List, Optional

# Schemas for CarJournalEntry
class CarJournalEntryBase(BaseModel):
    total_charged_kwh: float
    car_id: int
    entity_id: int

class CarJournalEntryCreate(CarJournalEntryBase):
    pass

class CarJournalEntry(CarJournalEntryBase):
    id: int

    class Config:
        from_attributes = True


# Schemas for MonthlyJournal
class MonthlyJournalBase(BaseModel):
    year: int
    month: int
    grid_consumption_low_kwh: float = 0.0
    grid_consumption_high_kwh: float = 0.0
    grid_feed_in_low_kwh: float = 0.0
    grid_feed_in_high_kwh: float = 0.0
    consumption_price_low_eur_kwh: float = 0.0
    consumption_price_high_eur_kwh: float = 0.0
    feed_in_tariff_low_eur_kwh: float = 0.0
    feed_in_tariff_high_eur_kwh: float = 0.0
    solar_production_kwh: float = 0.0
    battery_charge_kwh: float = 0.0
    battery_discharge_kwh: float = 0.0
    monthly_prepayment_eur: float = 0.0
    car_journal_entries: List[CarJournalEntryCreate] = []

class MonthlyJournalCreate(MonthlyJournalBase):
    pass

class MonthlyJournalUpdate(MonthlyJournalBase):
    pass

# This schema will be used for the API response, including calculated fields
class MonthlyJournal(MonthlyJournalBase):
    id: int
    car_journal_entries: List[CarJournalEntry] = []

    # Calculated Financials
    total_consumption_cost_excl_vat: float
    total_consumption_cost_incl_vat: float
    total_feed_in_revenue: float
    total_car_reimbursement_eur: float
    net_balance: float # "Naar eigen rekening"

    # Calculated Energy Flows
    self_consumption_kwh: float
    self_sufficiency_pct: float
    total_consumption_kwh: float

    class Config:
        from_attributes = True
