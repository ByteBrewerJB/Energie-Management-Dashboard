from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import models
from app.schemas.tariff import TariffCreate, TariffUpdate


def get(db: Session, tariff_id: int) -> Optional[models.Tariff]:
    """
    Retrieves a single tariff by its ID.
    """
    return db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tariff]:
    """
    Retrieves multiple tariffs with pagination.
    """
    return db.query(models.Tariff).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: TariffCreate) -> models.Tariff:
    """
    Creates a new tariff record.
    """
    db_obj = models.Tariff(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Tariff, obj_in: TariffUpdate
) -> models.Tariff:
    """
    Updates an existing tariff record.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, tariff_id: int) -> Optional[models.Tariff]:
    """
    Removes a tariff record from the database.
    """
    db_obj = db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
