from pydantic import BaseModel
from typing import Dict, Any
from .metrics import MonthlyMetricInDB

class EnergyFlowResult(BaseModel):
    self_consumption_kwh: float
    total_consumption_kwh: float
    home_consumption_kwh: float
    self_sufficiency_ratio: float

class FinancialResult(BaseModel):
    import_costs_ex_vat: float
    export_revenue_ex_vat: float
    net_monthly_result_ex_vat: float
    import_costs_inc_vat: float
    export_revenue_inc_vat: float
    net_monthly_result_inc_vat: float

class MonthlyAnalysisResult(BaseModel):
    """
    A comprehensive schema for a single month's analysis, combining the
    raw metric data with calculated energy and financial results.
    """
    metric: MonthlyMetricInDB
    energy_flow: EnergyFlowResult
    financials: FinancialResult

    class Config:
        orm_mode = True
