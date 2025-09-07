from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Any

from app.db.session import get_db
from app.schemas.analysis import MonthlyAnalysisResult
from app.crud import crud_analysis, crud_tariffs
from app.services import energy_calculations, financial_calculations

router = APIRouter()

@router.get("/analysis/timeseries", response_model=List[MonthlyAnalysisResult])
def get_timeseries_analysis(
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Start date for analysis (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date for analysis (YYYY-MM-DD)"),
):
    """
    Performs a time-series analysis of energy and financial data.
    """
    metrics = crud_analysis.get_metrics_for_period(db, start_date, end_date)
    if not metrics:
        raise HTTPException(status_code=404, detail="No monthly metrics found for the selected period.")

    results: List[Any] = []

    for metric in metrics:
        # Use the new function to get tariff by year and month
        tariff = crud_tariffs.get_by_year_and_month(db, year=metric.period_start.year, month=metric.period_start.month)
        if not tariff:
            # Skip months without a tariff, or raise an error. Skipping is more robust.
            continue

        # Use the new, refactored service functions
        energy_flow_data = energy_calculations.calculate_energy_flow(metric)
        financial_data = financial_calculations.calculate_energy_financials(metric, tariff)

        results.append({
            "metric": metric,
            "energy_flow": energy_flow_data,
            "financials": financial_data,
        })

    return results
