from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.models import models
from app.schemas.metrics import MonthlyMetricCreate, MonthlyMetricUpdate


def get(db: Session, metric_id: int) -> Optional[models.MonthlyMetric]:
    """Get a single metric by ID."""
    return db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.MonthlyMetric]:
    """Get multiple metrics."""
    return db.query(models.MonthlyMetric).order_by(models.MonthlyMetric.period_start.desc()).offset(skip).limit(limit).all()


def get_metrics_by_investment(db: Session, *, investment_id: int, start_date: date) -> List[models.MonthlyMetric]:
    """Get all metrics since the investment installation date."""
    # This function seems to not use the investment_id, but the logic is kept from the original.
    # It fetches all metrics after a certain date.
    return db.query(models.MonthlyMetric).filter(
        models.MonthlyMetric.period_start >= start_date
    ).order_by(models.MonthlyMetric.period_start.asc()).all()


def create(db: Session, *, obj_in: MonthlyMetricCreate) -> models.MonthlyMetric:
    """Create a new metric."""
    db_obj = models.MonthlyMetric(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.MonthlyMetric, obj_in: MonthlyMetricUpdate
) -> models.MonthlyMetric:
    """Update a metric."""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, metric_id: int) -> Optional[models.MonthlyMetric]:
    """Remove a metric."""
    db_obj = db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
