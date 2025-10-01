from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas.battery import BatteryCreate, BatteryUpdate


def get(db: Session, battery_id: int) -> Optional[models.Battery]:
    """
    Retrieves a single battery installation by its ID.
    """
    return db.query(models.Battery).filter(models.Battery.id == battery_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Battery]:
    """
    Retrieves multiple battery installations with pagination.
    """
    return db.query(models.Battery).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: BatteryCreate) -> models.Battery:
    """
    Creates a new battery installation record.
    """
    db_obj = models.Battery(
        name=obj_in.name,
        purchase_date=obj_in.purchase_date,
        purchase_cost_eur=obj_in.purchase_cost_eur,
        brand=getattr(obj_in, 'brand', None),
        capacity_kwh=obj_in.capacity_kwh
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Battery, obj_in: BatteryUpdate
) -> models.Battery:
    """
    Updates an existing battery installation record.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, battery_id: int) -> Optional[models.Battery]:
    """
    Removes a battery installation record from the database.
    """
    db_obj = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
