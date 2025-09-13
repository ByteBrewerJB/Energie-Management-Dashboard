from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.services import roi_service
from app.schemas.roi import SolarPanelROI, BatteryROI
from app.models.user import User

router = APIRouter()


@router.get("/solar_panels/{solar_panel_id}", response_model=SolarPanelROI)
def get_solar_panel_roi_endpoint(
    solar_panel_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve the ROI status for a specific solar panel installation.
    """
    roi_data = roi_service.get_solar_panel_roi(db, solar_panel_id=solar_panel_id)
    if not roi_data:
        raise HTTPException(status_code=404, detail="SolarPanel not found")
    return roi_data


@router.get("/batteries/{battery_id}", response_model=BatteryROI)
def get_battery_roi_endpoint(
    battery_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve the ROI status for a specific battery installation.
    """
    roi_data = roi_service.get_battery_roi(db, battery_id=battery_id)
    if not roi_data:
        raise HTTPException(status_code=404, detail="Battery not found")
    return roi_data
