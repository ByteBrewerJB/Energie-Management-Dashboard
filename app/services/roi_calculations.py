from sqlalchemy.orm import Session
from app.crud import crud_investments, crud_metrics, crud_tariffs
from app.services import energy_calculations, financial_calculations
from app.schemas.roi import ROIStatus, ROIMethodResult
from app.models.models import Investment, MonthlyMetric, Tariff

def calculate_roi_status(db: Session, investment_id: int) -> ROIStatus:
    investment = crud_investments.get_investment(db, investment_id)
    if not investment:
        return None

    metrics = crud_metrics.get_metrics_by_investment(db, investment_id=investment_id, start_date=investment.installation_date)

    cumulative_savings_m1 = 0.0
    cumulative_savings_m2 = 0.0

    for metric in metrics:
        tariff = crud_tariffs.get_active_tariff(db, on_date=metric.period_start)
        if not tariff:
            continue

        # Method 1
        energy_flow = energy_calculations.calculate_energy_flow(metric)
        financials = financial_calculations.calculate_financials(metric, tariff)
        avoided_costs = energy_flow['self_consumption_kwh'] * float(tariff.purchase_high_eur_kwh)
        revenue = financials['export_revenue_ex_vat']
        monthly_value_m1 = avoided_costs + revenue
        cumulative_savings_m1 += monthly_value_m1

        # Method 2
        if tariff.fixed_roi_rate_eur_kwh:
            monthly_value_m2 = metric.production_total_kwh * float(tariff.fixed_roi_rate_eur_kwh)
            cumulative_savings_m2 += monthly_value_m2

    total_cost = float(investment.total_cost_eur)

    # Results for Method 1
    remaining_balance_m1 = total_cost - cumulative_savings_m1
    progress_percentage_m1 = (cumulative_savings_m1 / total_cost) * 100 if total_cost > 0 else 0
    result_m1 = ROIMethodResult(
        cumulative_savings=cumulative_savings_m1,
        remaining_balance=remaining_balance_m1,
        progress_percentage=progress_percentage_m1
    )

    # Results for Method 2
    remaining_balance_m2 = total_cost - cumulative_savings_m2
    progress_percentage_m2 = (cumulative_savings_m2 / total_cost) * 100 if total_cost > 0 else 0
    result_m2 = ROIMethodResult(
        cumulative_savings=cumulative_savings_m2,
        remaining_balance=remaining_balance_m2,
        progress_percentage=progress_percentage_m2
    )

    return ROIStatus(method_1=result_m1, method_2=result_m2)
