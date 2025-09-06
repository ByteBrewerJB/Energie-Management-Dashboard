from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.roi import ROIMethodResult, ROIStatus
from app.services import roi_calculations

router = APIRouter()


@router.get("/roi/{investment_id}", response_model=ROIMethodResult)
def get_roi_status(investment_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the ROI status for a specific investment.

    This endpoint now returns the result of Method 1 for ROI calculation.
    """
    roi_status: ROIStatus | None = roi_calculations.calculate_roi_status(
        db, investment_id
    )
    if not roi_status:
        raise HTTPException(
            status_code=404, detail="Investment not found or no metrics available."
        )
    return roi_status.method_1
