from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api import deps
from app.schemas.roi import ROIStatus
from app.services import roi_calculations

router = APIRouter()


@router.get("/solar_panels/{solar_panel_id}", response_model=ROIStatus)
def get_solar_panel_roi_status(
    solar_panel_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieves the ROI status for a specific solar panel installation.
    """
    roi_status = roi_calculations.calculate_solar_panel_roi(db, solar_panel_id=solar_panel_id)
    if not roi_status:
        raise HTTPException(
            status_code=404, detail="Solar panel installation not found or no metrics available."
        )
    return roi_status


@router.get("/batteries/{battery_id}", response_model=ROIStatus)
def get_battery_roi_status(
    battery_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieves the ROI status for a specific battery installation.
    """
    roi_status = roi_calculations.calculate_battery_roi(db, battery_id=battery_id)
    if not roi_status:
        raise HTTPException(
            status_code=404, detail="Battery installation not found or no metrics available."
        )
    return roi_status
