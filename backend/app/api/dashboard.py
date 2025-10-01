from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, get_db_session
from ..models.user import User
from ..schemas.dashboard import DashboardResponse, ROIProgress
from ..services.dashboard import get_dashboard_data
from ..services.roi import calculate_roi

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    target_year = year or datetime.utcnow().year
    return get_dashboard_data(db, current_user.id, target_year)


@router.get("/roi", response_model=ROIProgress)
def get_roi(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ROIProgress:
    return calculate_roi(db, current_user.id)
