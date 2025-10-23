from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import models
from app.schemas.car import CarCreate, CarUpdate


def get(db: Session, car_id: int) -> Optional[models.Car]:
    """
    Retrieves a single car by its ID.
    """
    return db.query(models.Car).filter(models.Car.id == car_id).first()


def get_by_name(db: Session, name: str) -> Optional[models.Car]:
    """
    Retrieves a single car by its name.
    """
    return db.query(models.Car).filter(models.Car.name == name).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Car]:
    """
    Retrieves multiple cars with pagination.
    """
    return db.query(models.Car).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: CarCreate) -> models.Car:
    """
    Creates a new car record.
    """
    db_obj = models.Car(
        name=obj_in.name,
        reimbursement_rate_eur_per_kwh=obj_in.reimbursement_rate_eur_per_kwh
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Car, obj_in: CarUpdate
) -> models.Car:
    """
    Updates an existing car record.
    """
    # Use Pydantic v2 .model_dump()
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, car_id: int) -> Optional[models.Car]:
    """
    Removes a car record from the database.
    """
    db_obj = db.query(models.Car).filter(models.Car.id == car_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
