from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.models import models
from app.schemas.tariff import TariffCreate, TariffUpdate


def get_active_tariff(db: Session, on_date: date) -> Optional[models.Tariff]:
    """
    Retrieves the active tariff for a given date.

    An active tariff is one where the given date is between the start_date and
    end_date. If end_date is null, it is considered to be ongoing.

    Args:
        db: The database session.
        on_date: The date to find an active tariff for.

    Returns:
        The active Tariff object if found, otherwise None.
    """
    return db.query(models.Tariff).filter(
        models.Tariff.start_date <= on_date,
        (models.Tariff.end_date >= on_date) | (models.Tariff.end_date.is_(None))
    ).order_by(models.Tariff.start_date.desc()).first()


def get(db: Session, tariff_id: int) -> Optional[models.Tariff]:
    """
    Retrieves a single tariff by its ID.

    Args:
        db: The database session.
        tariff_id: The ID of the tariff to retrieve.

    Returns:
        The Tariff object if found, otherwise None.
    """
    return db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tariff]:
    """
    Retrieves multiple tariffs with pagination.

    Args:
        db: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A list of Tariff objects, ordered by start_date descending.
    """
    return db.query(models.Tariff).order_by(models.Tariff.start_date.desc()).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: TariffCreate) -> models.Tariff:
    """
    Creates a new tariff record.

    Args:
        db: The database session.
        obj_in: A TariffCreate schema object with the data for the new tariff.

    Returns:
        The newly created Tariff object.
    """
    db_obj = models.Tariff(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Tariff, obj_in: TariffUpdate
) -> models.Tariff:
    """
    Updates an existing tariff record.

    Args:
        db: The database session.
        db_obj: The existing Tariff object to update.
        obj_in: A TariffUpdate schema object with the new data.

    Returns:
        The updated Tariff object.
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, tariff_id: int) -> Optional[models.Tariff]:
    """
    Removes a tariff record from the database.

    Args:
        db: The database session.
        tariff_id: The ID of the tariff to remove.

    Returns:
        The removed Tariff object, or None if it was not found.
    """
    db_obj = db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
