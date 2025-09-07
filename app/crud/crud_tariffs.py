from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas.tariff import TariffCreate, TariffUpdate


def get_by_year_and_month(db: Session, year: int, month: int) -> Optional[models.Tariff]:
    """
    Retrieves the tariff for a given year and month.
    """
    return db.query(models.Tariff).filter(models.Tariff.year == year, models.Tariff.month == month).first()


def get(db: Session, tariff_id: int) -> Optional[models.Tariff]:
    """
    Retrieves a single tariff by its ID.
    """
    return db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tariff]:
    """
    Retrieves multiple tariffs with pagination, ordered by year and month descending.
    """
    return db.query(models.Tariff).order_by(models.Tariff.year.desc(), models.Tariff.month.desc()).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: TariffCreate) -> models.Tariff:
    """
    Creates a new tariff record.
    """
    db_obj = models.Tariff(
        year=obj_in.year,
        month=obj_in.month,
        consumption_price_low_eur_kwh=obj_in.consumption_price_low_eur_kwh,
        consumption_price_high_eur_kwh=obj_in.consumption_price_high_eur_kwh,
        feed_in_tariff_low_eur_kwh=obj_in.feed_in_tariff_low_eur_kwh,
        feed_in_tariff_high_eur_kwh=obj_in.feed_in_tariff_high_eur_kwh,
        vat_percentage=obj_in.vat_percentage,
        fixed_roi_rate_eur_kwh=obj_in.fixed_roi_rate_eur_kwh
    )
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
    """
    db_obj = db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
