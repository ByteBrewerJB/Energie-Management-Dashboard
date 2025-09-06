from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.db.session import get_db
from app.schemas.analysis import FullAnalysisResponse, MonthlyAnalysis, EnergyFlowResult, FinancialResult, RoiResult
from app.crud import crud_analysis
from app.models.models import MonthlyMetric, Tariff

router = APIRouter()

def get_tariff_for_month(month_date: date, tariffs: List[Tariff]) -> Tariff | None:
    """Finds the correct tariff for a given month from a list of tariffs."""
    for tariff in tariffs:
        is_current = tariff.end_date is None and month_date >= tariff.start_date
        is_in_range = tariff.end_date and tariff.start_date <= month_date <= tariff.end_date
        if is_current or is_in_range:
            return tariff
    return None

@router.get("/analysis", response_model=FullAnalysisResponse)
def get_full_analysis(
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Start date for analysis (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date for analysis (YYYY-MM-DD)"),
    roi_method: str = Query("standard", description="ROI calculation method: 'standard' or 'excel'")
):
    """
    Performs a full energy, financial, and ROI analysis for a given period.
    """
    # 1. Fetch all necessary data from the database
    investment = crud_analysis.get_investment(db)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment data not found. Please add it first.")

    metrics = crud_analysis.get_metrics_for_period(db, start_date, end_date)
    tariffs = crud_analysis.get_tariffs_for_period(db, start_date, end_date)

    if not metrics:
        raise HTTPException(status_code=404, detail="No monthly metrics found for the selected period.")

    monthly_analyses: List[MonthlyAnalysis] = []
    total_earned_for_roi = 0.0

    # 2. Process each month's metrics
    for metric in metrics:
        # --- Energy Flow Analysis ---
        self_consumption_kwh = metric.production_total_kwh - metric.export_total_kwh
        total_consumption_kwh = (metric.import_low_kwh + metric.import_high_kwh) + self_consumption_kwh
        home_consumption_kwh = total_consumption_kwh - metric.consumption_ev_kwh
        self_sufficiency_percent = (self_consumption_kwh / total_consumption_kwh) * 100 if total_consumption_kwh > 0 else 0
        self_consumption_ratio_percent = (self_consumption_kwh / metric.production_total_kwh) * 100 if metric.production_total_kwh > 0 else 0

        energy_flow = EnergyFlowResult(
            self_consumption_kwh=self_consumption_kwh,
            total_consumption_kwh=total_consumption_kwh,
            home_consumption_kwh=home_consumption_kwh,
            self_sufficiency_percent=self_sufficiency_percent,
            self_consumption_ratio_percent=self_consumption_ratio_percent
        )

        # --- Financial Management ---
        tariff = get_tariff_for_month(metric.period_start, tariffs)
        if not tariff:
            continue

        purchase_costs = (metric.import_low_kwh * float(tariff.purchase_low_eur_kwh)) + \
                         (metric.import_high_kwh * float(tariff.purchase_high_eur_kwh))
        feed_in_revenue = metric.export_total_kwh * float(tariff.sale_eur_kwh)
        net_result = feed_in_revenue - purchase_costs

        financials = FinancialResult(
            purchase_costs=purchase_costs,
            feed_in_revenue=feed_in_revenue,
            net_result=net_result
        )

        # --- ROI Calculation (per month contribution) ---
        if roi_method == "standard":
            avoided_costs = self_consumption_kwh * float(tariff.purchase_low_eur_kwh)
            monthly_roi_value = avoided_costs + feed_in_revenue
        elif roi_method == "excel":
            monthly_roi_value = metric.production_total_kwh * float(tariff.fixed_roi_rate_eur_kwh) if tariff.fixed_roi_rate_eur_kwh else 0
        else:
            monthly_roi_value = 0

        total_earned_for_roi += monthly_roi_value

        monthly_analyses.append(MonthlyAnalysis(
            period=metric.period_start.strftime("%Y-%m"),
            energy_flow=energy_flow,
            financials=financials
        ))

    # 3. Final ROI Calculation
    total_investment = float(investment.total_cost_eur)
    remaining_balance = total_investment - total_earned_for_roi

    roi = RoiResult(
        calculation_method=roi_method,
        total_investment=total_investment,
        total_earned=total_earned_for_roi,
        remaining_balance=remaining_balance
    )

    return FullAnalysisResponse(roi=roi, monthly_data=monthly_analyses)
