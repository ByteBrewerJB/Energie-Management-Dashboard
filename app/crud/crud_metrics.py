from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.models import models
from app.schemas.metrics import MonthlyMetricCreate, MonthlyMetricUpdate


def get(db: Session, metric_id: int) -> Optional[models.MonthlyMetric]:
    """
    Retrieves a single monthly metric by its ID.
    """
    return db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()


def get_by_period_start(db: Session, period_start: date) -> Optional[models.MonthlyMetric]:
    """
    Retrieves a single monthly metric by its period_start date.
    """
    return db.query(models.MonthlyMetric).filter(models.MonthlyMetric.period_start == period_start).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.MonthlyMetric]:
    """
    Retrieves multiple monthly metrics with pagination.
    """
    return db.query(models.MonthlyMetric).order_by(models.MonthlyMetric.period_start.desc()).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: MonthlyMetricCreate) -> models.MonthlyMetric:
    """
    Creates a new monthly metric record.
    """
    db_obj = models.MonthlyMetric(
        period_start=obj_in.period_start,
        account_name=obj_in.account_name,
        production_total_kwh=obj_in.production_total_kwh,
        grid_consumption_low_kwh=obj_in.grid_consumption_low_kwh,
        grid_consumption_high_kwh=obj_in.grid_consumption_high_kwh,
        grid_feed_in_low_kwh=obj_in.grid_feed_in_low_kwh,
        grid_feed_in_high_kwh=obj_in.grid_feed_in_high_kwh,
        battery_charge_kwh=obj_in.battery_charge_kwh,
        battery_discharge_kwh=obj_in.battery_discharge_kwh,
        monthly_prepayment_eur=obj_in.monthly_prepayment_eur,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.MonthlyMetric, obj_in: MonthlyMetricUpdate
) -> models.MonthlyMetric:
    """
    Updates an existing monthly metric record.
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
    """
    db_obj = db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
