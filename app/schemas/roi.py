from pydantic import BaseModel
from typing import List, Optional

class MonthlyROIBreakdown(BaseModel):
    year: int
    month: int
    revenue: float
    avoided_cost: float
    net_savings: float

class ROIBase(BaseModel):
    total_investment: float
    total_savings: float
    roi_percentage: float
    payback_period_years: Optional[float] = None
    monthly_breakdown: List[MonthlyROIBreakdown]

class SolarPanelROI(ROIBase):
    pass

class BatteryROIMethod(BaseModel):
    charging_costs: float
    avoided_costs: float
    net_savings: float

class BatteryROI(ROIBase):
    # The spec mentions method_2 is not implemented and returns zero values.
    # I will create the structure for it anyway.
    method_1: BatteryROIMethod # Energy Arbitrage
    method_2: BatteryROIMethod # Not implemented
