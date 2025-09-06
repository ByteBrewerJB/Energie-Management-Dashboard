from pydantic import BaseModel
from typing import Dict

class ROIMethodResult(BaseModel):
    cumulative_savings: float
    remaining_balance: float
    progress_percentage: float

class ROIStatus(BaseModel):
    method_1: ROIMethodResult
    method_2: ROIMethodResult
