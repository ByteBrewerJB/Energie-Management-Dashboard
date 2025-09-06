from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.models import SolarInvestmentOption
from app.schemas.solar_investment import SolarInvestmentCreate, SolarInvestmentUpdate

def get(db: Session, id: UUID) -> Optional[SolarInvestmentOption]:
    return db.query(SolarInvestmentOption).filter(SolarInvestmentOption.id == id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[SolarInvestmentOption]:
    return db.query(SolarInvestmentOption).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: SolarInvestmentCreate) -> SolarInvestmentOption:
    db_obj = SolarInvestmentOption(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
    db: Session, *, db_obj: SolarInvestmentOption, obj_in: SolarInvestmentUpdate
) -> SolarInvestmentOption:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, id: UUID) -> Optional[SolarInvestmentOption]:
    obj = db.query(SolarInvestmentOption).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
