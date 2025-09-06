from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from typing import List

from app.models.models import Investment, Tariff, MonthlyMetric

def get_investment(db: Session) -> Investment | None:
    """Retrieves the first investment record from the database.

    Assumes a single investment for the scope of this project.

    Args:
        db: The database session.

    Returns:
        The first Investment object found, or None if no investments exist.
    """
    return db.query(Investment).first()


def get_tariffs_for_period(db: Session, start_date: date, end_date: date) -> List[Tariff]:
    """Retrieves all tariffs active within a given date range.

    This includes tariffs that start, end, or are fully contained within the
    period.

    Args:
        db: The database session.
        start_date: The start date of the period.
        end_date: The end date of the period.

    Returns:
        A list of Tariff objects active during the specified period.
    """
    return db.query(Tariff).filter(
        or_(
            # Tariff starts within the period
            and_(Tariff.start_date >= start_date, Tariff.start_date <= end_date),
            # Tariff ends within the period
            and_(Tariff.end_date >= start_date, Tariff.end_date <= end_date),
            # Tariff encapsulates the entire period
            and_(Tariff.start_date <= start_date, Tariff.end_date >= end_date),
            # Tariff is current and started before the end of the period
            and_(Tariff.start_date <= end_date, Tariff.end_date == None)
        )
    ).order_by(Tariff.start_date).all()

def get_metrics_for_period(db: Session, start_date: date, end_date: date) -> List[MonthlyMetric]:
    """Retrieves all monthly metrics within a specified date range.

    Args:
        db: The database session.
        start_date: The start date of the period (inclusive).
        end_date: The end date of the period (inclusive).

    Returns:
        A list of MonthlyMetric objects for the specified period.
    """
    return db.query(MonthlyMetric).filter(
        and_(
            MonthlyMetric.period_start >= start_date,
            MonthlyMetric.period_start <= end_date
        )
    ).order_by(MonthlyMetric.period_start).all()
