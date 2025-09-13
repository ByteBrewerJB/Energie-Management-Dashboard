from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.solar_panel import SolarPanel
from app.schemas.solar_panel import SolarPanelCreate, SolarPanelUpdate


def get_solar_panel(db: Session, solar_panel_id: int) -> Optional[SolarPanel]:
    return db.query(SolarPanel).filter(SolarPanel.id == solar_panel_id).first()


def get_solar_panels(db: Session, skip: int = 0, limit: int = 100) -> List[SolarPanel]:
    return db.query(SolarPanel).offset(skip).limit(limit).all()


def create_solar_panel(db: Session, solar_panel: SolarPanelCreate) -> SolarPanel:
    db_solar_panel = SolarPanel(**solar_panel.model_dump())
    db.add(db_solar_panel)
    db.commit()
    db.refresh(db_solar_panel)
    return db_solar_panel


def update_solar_panel(db: Session, solar_panel_id: int, solar_panel_in: SolarPanelUpdate) -> Optional[SolarPanel]:
    db_solar_panel = get_solar_panel(db, solar_panel_id)
    if db_solar_panel:
        update_data = solar_panel_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_solar_panel, key, value)
        db.commit()
        db.refresh(db_solar_panel)
    return db_solar_panel


def delete_solar_panel(db: Session, solar_panel_id: int) -> Optional[SolarPanel]:
    db_solar_panel = get_solar_panel(db, solar_panel_id)
    if db_solar_panel:
        db.delete(db_solar_panel)
        db.commit()
    return db_solar_panel
