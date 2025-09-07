from app.models.models import MonthlyMetric
from decimal import Decimal

def calculate_energy_flow(metric: MonthlyMetric) -> dict:
    """
    Calculates key energy flow metrics based on a MonthlyMetric record.

    Args:
        metric: A MonthlyMetric object for a specific month.

    Returns:
        A dictionary with the calculated energy flow values.
    """
    # Use Decimal for precision, defaulting None to 0
    production_total_kwh = Decimal(metric.production_total_kwh or 0)
    grid_feed_in_low_kwh = Decimal(metric.grid_feed_in_low_kwh or 0)
    grid_feed_in_high_kwh = Decimal(metric.grid_feed_in_high_kwh or 0)
    grid_consumption_low_kwh = Decimal(metric.grid_consumption_low_kwh or 0)
    grid_consumption_high_kwh = Decimal(metric.grid_consumption_high_kwh or 0)
    battery_charge_kwh = Decimal(metric.battery_charge_kwh or 0)

    total_grid_feed_in_kwh = grid_feed_in_low_kwh + grid_feed_in_high_kwh

    # Self-consumption is the produced energy that was not exported to the grid.
    self_consumption_kwh = production_total_kwh - total_grid_feed_in_kwh

    # Total consumption is the energy from the grid plus what was self-consumed.
    total_consumption_kwh = (grid_consumption_low_kwh + grid_consumption_high_kwh) + self_consumption_kwh

    # Home consumption is what's left after battery charging is accounted for.
    # Car charging is now handled separately and is not part of this calculation.
    home_consumption_kwh = total_consumption_kwh - battery_charge_kwh

    if total_consumption_kwh > 0:
        self_sufficiency_ratio = self_consumption_kwh / total_consumption_kwh
    else:
        self_sufficiency_ratio = Decimal(0)

    return {
        "self_consumption_kwh": self_consumption_kwh,
        "total_consumption_kwh": total_consumption_kwh,
        "home_consumption_kwh": home_consumption_kwh,
        "self_sufficiency_ratio": self_sufficiency_ratio,
        "total_grid_feed_in_kwh": total_grid_feed_in_kwh,
    }
