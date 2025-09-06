from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import MonthlyMetric
from app.schemas.forecast import ForecastResult, MonthlyAverage, Forecast
from datetime import date, timedelta


def get_production_forecast(db: Session) -> ForecastResult:
    """
    Generates a 12-month production forecast based on historical monthly averages.

    This function queries the database for historical monthly production data,
    calculates the average production for each month, and then uses these
    averages to forecast production for the next 12 months.

    Args:
        db: The database session.

    Returns:
        A ForecastResult object containing both the historical monthly averages
        and the 12-month forecast.
    """
    # Calculate historical monthly averages
    monthly_averages_query = db.query(
        func.extract('month', MonthlyMetric.period_start).label('month'),
        func.avg(MonthlyMetric.production_total_kwh).label('average_production')
    ).group_by('month').all()

    historical_averages = [MonthlyAverage(month=row.month, average_production=row.average_production) for row in monthly_averages_query]

    # Create a dictionary for easy lookup
    average_map = {avg.month: avg.average_production for avg in historical_averages}

    # Generate 12-month forecast
    forecast_list = []
    today = date.today()
    for i in range(12):
        future_date = today + timedelta(days=30 * i) # Approximate
        month = future_date.month
        year = future_date.year

        predicted_production = average_map.get(month, 0) # Default to 0 if no historical data for a month

        forecast_list.append(Forecast(
            month=month,
            year=year,
            predicted_production=predicted_production
        ))

    return ForecastResult(
        historical_averages=historical_averages,
        forecast=forecast_list
    )
