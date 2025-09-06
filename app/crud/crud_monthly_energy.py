from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.models import MonthlyEnergy
from app.schemas.monthly_energy import MonthlyEnergyCreate, MonthlyEnergyUpdate

def get(db: Session, id: UUID) -> Optional[MonthlyEnergy]:
    return db.query(MonthlyEnergy).filter(MonthlyEnergy.id == id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[MonthlyEnergy]:
    return db.query(MonthlyEnergy).order_by(MonthlyEnergy.year, MonthlyEnergy.month).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: MonthlyEnergyCreate) -> MonthlyEnergy:
    db_obj = MonthlyEnergy(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
    db: Session, *, db_obj: MonthlyEnergy, obj_in: MonthlyEnergyUpdate
) -> MonthlyEnergy:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, id: UUID) -> Optional[MonthlyEnergy]:
    obj = db.query(MonthlyEnergy).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
