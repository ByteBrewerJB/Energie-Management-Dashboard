from typing import List

from pydantic import BaseModel


class MonthlyKPI(BaseModel):
    month: int
    month_label: str
    net_balance_eur: float
    self_sufficiency_pct: float
    total_production_kwh: float
    total_consumption_kwh: float
    savings_eur: float


class MonthlyFinancials(BaseModel):
    month: int
    consumption_costs_eur: float
    feed_in_revenue_eur: float
    net_energy_costs_eur: float
    advance_payment_eur: float
    car_reimbursement_eur: float
    final_settlement_eur: float


class EnergyBalanceEntry(BaseModel):
    month: int
    net_import_kwh: float
    self_consumption_kwh: float
    net_export_kwh: float


class ConsumptionSplitEntry(BaseModel):
    month: int
    household_kwh: float
    ev_kwh: float


class ProductionComparisonEntry(BaseModel):
    month: int
    actual_production_kwh: float
    expected_production_kwh: float


class DashboardResponse(BaseModel):
    year: int
    kpis: List[MonthlyKPI]
    financials: List[MonthlyFinancials]
    energy_balance: List[EnergyBalanceEntry]
    consumption_split: List[ConsumptionSplitEntry]
    production_vs_expectation: List[ProductionComparisonEntry]


class ROIProgress(BaseModel):
    total_investment_eur: float
    total_savings_eur: float
    progress_ratio: float
