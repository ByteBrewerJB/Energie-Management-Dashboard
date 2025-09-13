from sqlalchemy.orm import Session
from app import crud
from app.schemas.roi import SolarPanelROI, BatteryROI, MonthlyROIBreakdown, BatteryROIMethod

def get_solar_panel_roi(db: Session, solar_panel_id: int) -> SolarPanelROI:
    solar_panel = crud.solar_panel.get_solar_panel(db, solar_panel_id)
    if not solar_panel:
        return None

    journal_entries = crud.journal.get_all_journals(db)

    total_savings = 0
    monthly_breakdown = []

    for entry in journal_entries:
        # 1. Revenue from Grid Feed-in
        revenue = (entry.grid_feed_in_low_kwh * entry.feed_in_tariff_low_eur_kwh) + \
                  (entry.grid_feed_in_high_kwh * entry.feed_in_tariff_high_eur_kwh)

        # 2. Avoided Costs from Self-Consumption
        # Self-consumption = Solar Production - Grid Feed-in
        self_consumption_kwh = entry.solar_production_kwh - (entry.grid_feed_in_low_kwh + entry.grid_feed_in_high_kwh)
        # Average electricity price for the month
        avg_price = (entry.consumption_price_low_eur_kwh + entry.consumption_price_high_eur_kwh) / 2
        avoided_cost = self_consumption_kwh * avg_price

        net_savings = revenue + avoided_cost
        total_savings += net_savings

        monthly_breakdown.append(MonthlyROIBreakdown(
            year=entry.year,
            month=entry.month,
            revenue=revenue,
            avoided_cost=avoided_cost,
            net_savings=net_savings
        ))

    roi_percentage = (total_savings / solar_panel.purchase_cost_eur) * 100 if solar_panel.purchase_cost_eur > 0 else 0

    return SolarPanelROI(
        total_investment=solar_panel.purchase_cost_eur,
        total_savings=total_savings,
        roi_percentage=roi_percentage,
        monthly_breakdown=monthly_breakdown
    )

def get_battery_roi(db: Session, battery_id: int) -> BatteryROI:
    battery = crud.battery.get_battery(db, battery_id)
    if not battery:
        return None

    journal_entries = crud.journal.get_all_journals(db)

    total_savings = 0
    monthly_breakdown = []

    for entry in journal_entries:
        # 1. Charging Costs (from grid only, solar is free)
        # This is a simplification. We don't know when the battery was charged from the grid.
        # Assuming all battery charging is from solar (cost=0) as per the spec's description.
        # "Charging from the user's own solar panels is considered free."
        # A more complex model would track grid charging vs solar charging.
        charging_costs = 0 # Simplified based on spec

        # 2. Avoided Costs from Discharging
        # Value of discharged energy, assuming it offsets high-peak consumption
        avoided_costs = entry.battery_discharge_kwh * entry.consumption_price_high_eur_kwh

        net_savings = avoided_costs - charging_costs
        total_savings += net_savings

        monthly_breakdown.append(MonthlyROIBreakdown(
            year=entry.year,
            month=entry.month,
            revenue=0, # Not applicable for battery
            avoided_cost=avoided_costs,
            net_savings=net_savings
        ))

    roi_percentage = (total_savings / battery.purchase_cost_eur) * 100 if battery.purchase_cost_eur > 0 else 0

    return BatteryROI(
        total_investment=battery.purchase_cost_eur,
        total_savings=total_savings,
        roi_percentage=roi_percentage,
        monthly_breakdown=monthly_breakdown,
        method_1=BatteryROIMethod(
            charging_costs=0, # Simplified
            avoided_costs=total_savings,
            net_savings=total_savings
        ),
        method_2=BatteryROIMethod(charging_costs=0, avoided_costs=0, net_savings=0) # Not implemented
    )
