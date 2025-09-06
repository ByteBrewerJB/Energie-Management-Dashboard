from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas.investment import InvestmentCreate, InvestmentUpdate


def get(db: Session, investment_id: int) -> Optional[models.Investment]:
    """Get a single investment by ID."""
    return db.query(models.Investment).filter(models.Investment.id == investment_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Investment]:
    """Get multiple investments."""
    return db.query(models.Investment).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: InvestmentCreate) -> models.Investment:
    """Create a new investment."""
    db_obj = models.Investment(
        description=obj_in.description,
        installation_date=obj_in.installation_date,
        total_cost_eur=obj_in.total_cost_eur,
        total_power_wp=obj_in.total_power_wp,
        estimated_annual_production_kwh=obj_in.estimated_annual_production_kwh,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Investment, obj_in: InvestmentUpdate
) -> models.Investment:
    """Update an investment."""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, investment_id: int) -> Optional[models.Investment]:
    """Remove an investment."""
    db_obj = db.query(models.Investment).filter(models.Investment.id == investment_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
