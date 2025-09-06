from pydantic import BaseModel
from typing import List, Optional

class EnergyFlowResult(BaseModel):
    """Schema for Energy Flow Analysis results."""
    self_consumption_kwh: float
    total_consumption_kwh: float
    home_consumption_kwh: float
    self_sufficiency_percent: float
    self_consumption_ratio_percent: float

class FinancialResult(BaseModel):
    """Schema for Financial Management results."""
    purchase_costs: float
    feed_in_revenue: float
    net_result: float

class RoiResult(BaseModel):
    """Schema for ROI Tracking results."""
    calculation_method: str
    total_investment: float
    total_earned: float
    remaining_balance: float

class MonthlyAnalysis(BaseModel):
    """A comprehensive schema combining all analysis results for a given period."""
    period: str # e.g., "2024-01"
    energy_flow: EnergyFlowResult
    financials: FinancialResult

    class Config:
        orm_mode = True

class FullAnalysisResponse(BaseModel):
    """The full response model including ROI and monthly breakdowns."""
    roi: RoiResult
    monthly_data: List[MonthlyAnalysis]

    class Config:
        orm_mode = True
