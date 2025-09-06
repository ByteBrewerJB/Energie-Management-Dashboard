from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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
    metric = crud_metrics.create_monthly_metric(db=db, metric=metric_in)
    return metric

@router.get("/metrics", response_model=List[MonthlyMetricInDB])
def read_metrics(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    metrics = crud_metrics.get_metrics(db, skip=skip, limit=limit)
    return metrics

@router.get("/metrics/{metric_id}", response_model=MonthlyMetricInDB)
def read_metric(
    *,
    db: Session = Depends(get_db),
    metric_id: int,
):
    metric = crud_metrics.get_metric(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric

@router.put("/metrics/{metric_id}", response_model=MonthlyMetricInDB)
def update_metric(
    *,
    db: Session = Depends(get_db),
    metric_id: int,
    metric_in: MonthlyMetricCreate,
):
    metric = crud_metrics.get_metric(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    metric = crud_metrics.update_metric(db=db, metric_id=metric_id, metric=metric_in)
    return metric

@router.delete("/metrics/{metric_id}", response_model=MonthlyMetricInDB)
def delete_metric(
    *,
    db: Session = Depends(get_db),
    metric_id: int,
):
    metric = crud_metrics.get_metric(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    metric = crud_metrics.delete_metric(db=db, metric_id=metric_id)
    return metric
