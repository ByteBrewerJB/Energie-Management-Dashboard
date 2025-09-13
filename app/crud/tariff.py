from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.tariff import Tariff
from app.schemas.tariff import TariffCreate, TariffUpdate


def get_tariff(db: Session, tariff_id: int) -> Optional[Tariff]:
    return db.query(Tariff).filter(Tariff.id == tariff_id).first()


def get_tariffs(db: Session, skip: int = 0, limit: int = 100) -> List[Tariff]:
    return db.query(Tariff).offset(skip).limit(limit).all()


def create_tariff(db: Session, tariff: TariffCreate) -> Tariff:
    db_tariff = Tariff(**tariff.model_dump())
    db.add(db_tariff)
    db.commit()
    db.refresh(db_tariff)
    return db_tariff


def update_tariff(db: Session, tariff_id: int, tariff_in: TariffUpdate) -> Optional[Tariff]:
    db_tariff = get_tariff(db, tariff_id)
    if db_tariff:
        update_data = tariff_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tariff, key, value)
        db.commit()
        db.refresh(db_tariff)
    return db_tariff


def delete_tariff(db: Session, tariff_id: int) -> Optional[Tariff]:
    db_tariff = get_tariff(db, tariff_id)
    if db_tariff:
        db.delete(db_tariff)
        db.commit()
    return db_tariff
