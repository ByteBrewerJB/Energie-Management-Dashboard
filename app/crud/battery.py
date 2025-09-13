from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.battery import Battery
from app.schemas.battery import BatteryCreate, BatteryUpdate


def get_battery(db: Session, battery_id: int) -> Optional[Battery]:
    return db.query(Battery).filter(Battery.id == battery_id).first()


def get_batteries(db: Session, skip: int = 0, limit: int = 100) -> List[Battery]:
    return db.query(Battery).offset(skip).limit(limit).all()


def create_battery(db: Session, battery: BatteryCreate) -> Battery:
    db_battery = Battery(**battery.model_dump())
    db.add(db_battery)
    db.commit()
    db.refresh(db_battery)
    return db_battery


def update_battery(db: Session, battery_id: int, battery_in: BatteryUpdate) -> Optional[Battery]:
    db_battery = get_battery(db, battery_id)
    if db_battery:
        update_data = battery_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_battery, key, value)
        db.commit()
        db.refresh(db_battery)
    return db_battery


def delete_battery(db: Session, battery_id: int) -> Optional[Battery]:
    db_battery = get_battery(db, battery_id)
    if db_battery:
        db.delete(db_battery)
        db.commit()
    return db_battery
