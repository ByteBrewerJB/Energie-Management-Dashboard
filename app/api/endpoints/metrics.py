from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.metrics import MonthlyMetricCreate, MonthlyMetricInDB
from app.crud import crud_metrics

router = APIRouter()

@router.post("/metrics", response_model=MonthlyMetricInDB)
def create_new_metric(
    *,
    db: Session = Depends(get_db),
    metric_in: MonthlyMetricCreate
):
    """
    Create a new monthly metric record.
    """
    # Here you could add checks to see if a metric for that period already exists
    metric = crud_metrics.create_monthly_metric(db=db, metric=metric_in)
    return metric
