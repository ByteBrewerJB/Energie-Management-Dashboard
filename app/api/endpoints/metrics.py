from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.metrics import MonthlyMetric, MonthlyMetricCreate, MonthlyMetricUpdate
from app.crud import crud_metrics
from app.models import models

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

    Args:
        db: The database session dependency.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.
        current_user: The authenticated user dependency.

    Returns:
        A list of MonthlyMetric objects.
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

    Args:
        db: The database session dependency.
        metric_in: The metric data from the request body.
        current_user: The authenticated user dependency.

    Returns:
        The newly created MonthlyMetric object.
    """
    # Check if a metric for this period already exists to prevent duplicates
    # existing_metric = crud_metrics.get_by_period(db, period=metric_in.period_start)
    # if existing_metric:
    #     raise HTTPException(status_code=400, detail="A metric for this period already exists.")
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

    Args:
        db: The database session dependency.
        metric_id: The ID of the metric to retrieve.
        current_user: The authenticated user dependency.

    Returns:
        The requested MonthlyMetric object.

    Raises:
        HTTPException: 404 Not Found if the metric does not exist.
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

    Args:
        db: The database session dependency.
        metric_id: The ID of the metric to update.
        metric_in: The new metric data from the request body.
        current_user: The authenticated user dependency.

    Returns:
        The updated MonthlyMetric object.

    Raises:
        HTTPException: 404 Not Found if the metric does not exist.
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

    Args:
        db: The database session dependency.
        metric_id: The ID of the metric to delete.
        current_user: The authenticated user dependency.

    Returns:
        The deleted MonthlyMetric object.

    Raises:
        HTTPException: 404 Not Found if the metric does not exist.
    """
    metric = crud_metrics.get(db, metric_id=metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    metric = crud_metrics.remove(db=db, metric_id=metric_id)
    return metric
