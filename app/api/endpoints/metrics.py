from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.metrics import MonthlyMetric, MonthlyMetricCreate, MonthlyMetricUpdate
from app.crud import crud_metrics

router = APIRouter()

@router.get("/metrics", response_model=List[MonthlyMetric])
def read_metrics(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all monthly metrics.
    """
    metrics = crud_metrics.get_multi(db, skip=skip, limit=limit)
    return metrics


@router.post("/metrics", response_model=MonthlyMetric, status_code=status.HTTP_201_CREATED)
def create_metric(
    *,
    db: Session = Depends(get_db),
    metric_in: MonthlyMetricCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new monthly metric.
    """
    # Check if a metric for this period already exists to prevent duplicates
    existing_metric = crud_metrics.get_by_period_start(db, period_start=metric_in.period_start)
    if existing_metric:
        raise HTTPException(status_code=400, detail="A metric for this period already exists.")
    metric = crud_metrics.create(db=db, obj_in=metric_in)
    return metric


@router.get("/metrics/{metric_id}", response_model=MonthlyMetric)
def read_metric(
    *,
    db: Session = Depends(get_db),
    metric_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific monthly metric by its ID.
    """
    metric = crud_metrics.get(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.put("/metrics/{metric_id}", response_model=MonthlyMetric)
def update_metric(
    *,
    db: Session = Depends(get_db),
    metric_id: int,
    metric_in: MonthlyMetricUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing monthly metric.
    """
    metric = crud_metrics.get(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    metric = crud_metrics.update(db=db, db_obj=metric, obj_in=metric_in)
    return metric


@router.delete("/metrics/{metric_id}", response_model=MonthlyMetric)
def delete_metric(
    *,
    db: Session = Depends(get_db),
    metric_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a monthly metric.
    """
    metric = crud_metrics.get(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    metric = crud_metrics.remove(db=db, metric_id=metric_id)
    return metric
