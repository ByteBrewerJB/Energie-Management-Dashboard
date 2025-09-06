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
    Performs a timeseries analysis of energy and financial data.
    """
    metrics = crud_analysis.get_metrics_for_period(db, start_date, end_date)
    if not metrics:
        raise HTTPException(status_code=404, detail="No monthly metrics found for the selected period.")

    results: List[Any] = []

    for metric in metrics:
        tariff = crud_tariffs.get_active_tariff(db, on_date=metric.period_start)
        if not tariff:
            # Or handle this case as you see fit, maybe skip the month or use a default tariff
            raise HTTPException(status_code=404, detail=f"No active tariff found for date {metric.period_start}")


        energy_flow_data = energy_calculations.calculate_energy_flow(metric)
        financial_data = financial_calculations.calculate_financials(metric, tariff)

        results.append({
            "metric": metric,
            "energy_flow": energy_flow_data,
            "financials": financial_data,
        })

    return results
