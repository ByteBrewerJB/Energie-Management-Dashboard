from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas.solar_panel import SolarPanelCreate, SolarPanelUpdate


def get(db: Session, solar_panel_id: int) -> Optional[models.SolarPanel]:
    """
    Retrieves a single solar panel installation by its ID.
    """
    return db.query(models.SolarPanel).filter(models.SolarPanel.id == solar_panel_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.SolarPanel]:
    """
    Retrieves multiple solar panel installations with pagination.
    """
    return db.query(models.SolarPanel).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: SolarPanelCreate) -> models.SolarPanel:
    """
    Creates a new solar panel installation record.
    """
    db_obj = models.SolarPanel(
        name=obj_in.name,
        purchase_date=obj_in.purchase_date,
        purchase_cost_eur=obj_in.purchase_cost_eur,
        total_power_wp=obj_in.total_power_wp,
        expected_annual_yield_kwh=obj_in.expected_annual_yield_kwh,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.SolarPanel, obj_in: SolarPanelUpdate
) -> models.SolarPanel:
    """
    Updates an existing solar panel installation record.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, solar_panel_id: int) -> Optional[models.SolarPanel]:
    """
    Removes a solar panel installation record from the database.
    """
    db_obj = db.query(models.SolarPanel).filter(models.SolarPanel.id == solar_panel_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
