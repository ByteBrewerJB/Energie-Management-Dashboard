from pydantic import BaseModel
from typing import Dict


class ROIMethodResult(BaseModel):
    """Schema for the result of a single ROI calculation method."""
    cumulative_savings: float
    remaining_balance: float
    progress_percentage: float


class ROIStatus(BaseModel):
    """Schema for the overall ROI status, containing results from multiple methods."""
    method_1: ROIMethodResult
    method_2: ROIMethodResult
