from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.models import models
from app.schemas.metrics import MonthlyMetricCreate, MonthlyMetricUpdate


def get(db: Session, metric_id: int) -> Optional[models.MonthlyMetric]:
    """
    Retrieves a single monthly metric by its ID.

    Args:
        db: The database session.
        metric_id: The ID of the metric to retrieve.

    Returns:
        The MonthlyMetric object if found, otherwise None.
    """
    return db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.MonthlyMetric]:
    """
    Retrieves multiple monthly metrics with pagination.

    Args:
        db: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A list of MonthlyMetric objects, ordered by period_start descending.
    """
    return db.query(models.MonthlyMetric).order_by(models.MonthlyMetric.period_start.desc()).offset(skip).limit(limit).all()


def get_metrics_by_investment(db: Session, *, investment_id: int, start_date: date) -> List[models.MonthlyMetric]:
    """
    Retrieves all metrics for an investment since its installation date.

    Note:
        The `investment_id` parameter is not directly used in the query filter
        but is kept for contextual clarity, implying that the metrics are related
        to a specific investment's timeframe.

    Args:
        db: The database session.
        investment_id: The ID of the investment.
        start_date: The installation date of the investment.

    Returns:
        A list of MonthlyMetric objects, ordered by period_start ascending.
    """
    # This function seems to not use the investment_id, but the logic is kept from the original.
    # It fetches all metrics after a certain date.
    return db.query(models.MonthlyMetric).filter(
        models.MonthlyMetric.period_start >= start_date
    ).order_by(models.MonthlyMetric.period_start.asc()).all()


def create(db: Session, *, obj_in: MonthlyMetricCreate) -> models.MonthlyMetric:
    """
    Creates a new monthly metric record.

    Args:
        db: The database session.
        obj_in: A MonthlyMetricCreate schema object with the data for the new
                metric.

    Returns:
        The newly created MonthlyMetric object.
    """
    db_obj = models.MonthlyMetric(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.MonthlyMetric, obj_in: MonthlyMetricUpdate
) -> models.MonthlyMetric:
    """
    Updates an existing monthly metric record.

    Args:
        db: The database session.
        db_obj: The existing MonthlyMetric object to update.
        obj_in: A MonthlyMetricUpdate schema object with the new data.

    Returns:
        The updated MonthlyMetric object.
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, metric_id: int) -> Optional[models.MonthlyMetric]:
    """
    Removes a monthly metric record from the database.

    Args:
        db: The database session.
        metric_id: The ID of the metric to remove.

    Returns:
        The removed MonthlyMetric object, or None if it was not found.
    """
    db_obj = db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
