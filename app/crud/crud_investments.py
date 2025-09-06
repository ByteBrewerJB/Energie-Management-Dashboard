from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas.investment import InvestmentCreate, InvestmentUpdate


def get(db: Session, investment_id: int) -> Optional[models.Investment]:
    """
    Retrieves a single investment by its ID.

    Args:
        db: The database session.
        investment_id: The ID of the investment to retrieve.

    Returns:
        The Investment object if found, otherwise None.
    """
    return db.query(models.Investment).filter(models.Investment.id == investment_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Investment]:
    """
    Retrieves multiple investments with pagination.

    Args:
        db: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A list of Investment objects.
    """
    return db.query(models.Investment).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: InvestmentCreate) -> models.Investment:
    """
    Creates a new investment record.

    Args:
        db: The database session.
        obj_in: An InvestmentCreate schema object with the data for the new
                investment.

    Returns:
        The newly created Investment object.
    """
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
    """
    Updates an existing investment record.

    Args:
        db: The database session.
        db_obj: The existing Investment object to update.
        obj_in: An InvestmentUpdate schema object with the new data.

    Returns:
        The updated Investment object.
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, investment_id: int) -> Optional[models.Investment]:
    """
    Removes an investment record from the database.

    Args:
        db: The database session.
        investment_id: The ID of the investment to remove.

    Returns:
        The removed Investment object, or None if it was not found.
    """
    db_obj = db.query(models.Investment).filter(models.Investment.id == investment_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
