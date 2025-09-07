from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal

from app.crud import crud_solar_panel, crud_battery, crud_journal
from app.models import models
from app.services import energy_calculations, financial_calculations
from app.schemas.roi import ROIMethodResult, ROIStatus

def calculate_solar_panel_roi(db: Session, solar_panel_id: int) -> ROIStatus:
    """
    Calculates the Return on Investment (ROI) status for a solar panel installation
    using the new MonthlyJournal data structure.
    """
    solar_panel = crud_solar_panel.get(db, solar_panel_id)
    if not solar_panel:
        return None

    # Fetch all journals since the installation date
    journals = db.query(models.MonthlyJournal).filter(
        models.MonthlyJournal.year >= solar_panel.purchase_date.year
    ).order_by(models.MonthlyJournal.year.asc(), models.MonthlyJournal.month.asc()).all()
    # This filter is imperfect if purchase month > journal month in the same year, but good enough for now.

    cumulative_savings = Decimal(0.0)

    for journal in journals:
        # 1. Calculate revenue from selling to the grid
        feed_in_revenue = (Decimal(journal.grid_feed_in_low_kwh) * journal.feed_in_tariff_low_eur_kwh) + \
                          (Decimal(journal.grid_feed_in_high_kwh) * journal.feed_in_tariff_high_eur_kwh)

        # 2. Calculate value of self-consumed energy (avoided cost)
        energy_flow = energy_calculations.calculate_energy_flow(journal)
        self_consumption_kwh = energy_flow["self_consumption_kwh"]

        total_grid_consumption_kwh = Decimal(journal.grid_consumption_low_kwh) + Decimal(journal.grid_consumption_high_kwh)
        total_consumption_cost = (Decimal(journal.grid_consumption_low_kwh) * journal.consumption_price_low_eur_kwh) + \
                                 (Decimal(journal.grid_consumption_high_kwh) * journal.consumption_price_high_eur_kwh)

        if total_grid_consumption_kwh > 0:
            avg_consumption_price = total_consumption_cost / total_grid_consumption_kwh
        else:
            avg_consumption_price = journal.consumption_price_high_eur_kwh # Fallback

        avoided_costs = self_consumption_kwh * avg_consumption_price

        monthly_savings = feed_in_revenue + avoided_costs
        cumulative_savings += monthly_savings

    total_cost = Decimal(solar_panel.purchase_cost_eur)
    remaining_balance = total_cost - cumulative_savings
    progress_percentage = (cumulative_savings / total_cost) * 100 if total_cost > 0 else 0

    result = ROIMethodResult(
        cumulative_savings=float(cumulative_savings),
        remaining_balance=float(remaining_balance),
        progress_percentage=float(progress_percentage)
    )

    return ROIStatus(method_1=result, method_2=ROIMethodResult(cumulative_savings=0, remaining_balance=0, progress_percentage=0))


def calculate_battery_roi(db: Session, battery_id: int) -> ROIStatus:
    """
    Calculates the Return on Investment (ROI) for a battery installation
    using the new MonthlyJournal data structure.
    """
    battery = crud_battery.get(db, battery_id)
    if not battery:
        return None

    journals = db.query(models.MonthlyJournal).filter(
        models.MonthlyJournal.year >= battery.purchase_date.year
    ).order_by(models.MonthlyJournal.year.asc(), models.MonthlyJournal.month.asc()).all()

    cumulative_savings = Decimal(0.0)

    for journal in journals:
        # Simplified arbitrage calculation
        avoided_cost = Decimal(journal.battery_discharge_kwh or 0) * journal.consumption_price_high_eur_kwh
        charge_cost = Decimal(journal.battery_charge_kwh or 0) * journal.consumption_price_low_eur_kwh

        monthly_savings = avoided_cost - charge_cost
        cumulative_savings += monthly_savings

    total_cost = Decimal(battery.purchase_cost_eur)
    remaining_balance = total_cost - cumulative_savings
    progress_percentage = (cumulative_savings / total_cost) * 100 if total_cost > 0 else 0

    result = ROIMethodResult(
        cumulative_savings=float(cumulative_savings),
        remaining_balance=float(remaining_balance),
        progress_percentage=float(progress_percentage)
    )

    return ROIStatus(method_1=result, method_2=ROIMethodResult(cumulative_savings=0, remaining_balance=0, progress_percentage=0))
