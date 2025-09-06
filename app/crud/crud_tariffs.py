from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.models import models
from app.schemas.tariff import TariffCreate, TariffUpdate


def get_active_tariff(db: Session, on_date: date) -> Optional[models.Tariff]:
    """
    Retrieves the active tariff for a given date.
    An active tariff is one where the given date is between the start_date and end_date.
    If end_date is null, it is considered to be ongoing.
    """
    return db.query(models.Tariff).filter(
        models.Tariff.start_date <= on_date,
        (models.Tariff.end_date >= on_date) | (models.Tariff.end_date.is_(None))
    ).order_by(models.Tariff.start_date.desc()).first()


def get(db: Session, tariff_id: int) -> Optional[models.Tariff]:
    """Get a single tariff by ID."""
    return db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tariff]:
    """Get multiple tariffs."""
    return db.query(models.Tariff).order_by(models.Tariff.start_date.desc()).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: TariffCreate) -> models.Tariff:
    """Create a new tariff."""
    db_obj = models.Tariff(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Tariff, obj_in: TariffUpdate
) -> models.Tariff:
    """Update a tariff."""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, tariff_id: int) -> Optional[models.Tariff]:
    """Remove a tariff."""
    db_obj = db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
