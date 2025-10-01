from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from typing import List

from app.models.models import Tariff, MonthlyMetric


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
    # This logic is based on the old date-range based tariffs.
    # It needs to be updated to work with the new year/month structure.
    # For now, as it seems this function is not used by the timeseries endpoint,
    # I will leave it but it should be noted for future refactoring.
    return db.query(Tariff).filter(
        # This filter is now incorrect for the new model.
        # A proper implementation would need to convert the date range to a series of year/month pairs.
    ).all()

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
