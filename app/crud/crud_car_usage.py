from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas.car_usage import CarUsageCreate, CarUsageUpdate


def get(db: Session, car_usage_id: int) -> Optional[models.CarUsage]:
    """
    Retrieves a single car usage record by its ID.
    """
    return db.query(models.CarUsage).filter(models.CarUsage.id == car_usage_id).first()


def get_multi_by_car(db: Session, car_id: int, skip: int = 0, limit: int = 100) -> List[models.CarUsage]:
    """
    Retrieves multiple car usage records for a specific car with pagination.
    """
    return db.query(models.CarUsage).filter(models.CarUsage.car_id == car_id).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: CarUsageCreate) -> models.CarUsage:
    """
    Creates a new car usage record.
    """
    db_obj = models.CarUsage(
        car_id=obj_in.car_id,
        period_start=obj_in.period_start,
        total_charged_kwh=obj_in.total_charged_kwh,
        reimbursement_rate_eur_per_kwh=obj_in.reimbursement_rate_eur_per_kwh,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.CarUsage, obj_in: CarUsageUpdate
) -> models.CarUsage:
    """
    Updates an existing car usage record.
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, car_usage_id: int) -> Optional[models.CarUsage]:
    """
    Removes a car usage record from the database.
    """
    db_obj = db.query(models.CarUsage).filter(models.CarUsage.id == car_usage_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
