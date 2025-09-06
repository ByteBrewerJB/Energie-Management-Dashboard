from sqlalchemy.orm import Session
from datetime import date

from app.models import models
from app.schemas import tariff as tariff_schema

def get_active_tariff(db: Session, on_date: date) -> models.Tariff | None:
    """
    Retrieves the active tariff for a given date.
    """
    return db.query(models.Tariff).filter(
        models.Tariff.start_date <= on_date,
        (models.Tariff.end_date >= on_date) | (models.Tariff.end_date == None)
    ).order_by(models.Tariff.start_date.desc()).first()

def get_tariff(db: Session, tariff_id: int):
    return db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()

def get_tariffs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tariff).offset(skip).limit(limit).all()

def create_tariff(db: Session, tariff: tariff_schema.TariffCreate):
    db_tariff = models.Tariff(**tariff.dict())
    db.add(db_tariff)
    db.commit()
    db.refresh(db_tariff)
    return db_tariff

def update_tariff(db: Session, tariff_id: int, tariff: tariff_schema.TariffCreate):
    db_tariff = db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()
    if db_tariff:
        for key, value in tariff.dict().items():
            setattr(db_tariff, key, value)
        db.commit()
        db.refresh(db_tariff)
    return db_tariff

def delete_tariff(db: Session, tariff_id: int):
    db_tariff = db.query(models.Tariff).filter(models.Tariff.id == tariff_id).first()
    if db_tariff:
        db.delete(db_tariff)
        db.commit()
    return db_tariff
