from app.models.models import MonthlyMetric

def calculate_energy_flow(metric: MonthlyMetric) -> dict:
    """
    Calculates energy flow values based on a MonthlyMetric record.

    Args:
        metric: A MonthlyMetric object.

    Returns:
        A dictionary with the calculated energy flow values.
    """
    self_consumption_kwh = metric.production_total_kwh - metric.export_total_kwh
    total_consumption_kwh = (metric.import_low_kwh + metric.import_high_kwh) + self_consumption_kwh

    # Subtract EV and battery charging from total consumption to find home consumption
    home_consumption_kwh = total_consumption_kwh - metric.consumption_ev_kwh - metric.battery_charge_kwh

    if total_consumption_kwh > 0:
        self_sufficiency_ratio = self_consumption_kwh / total_consumption_kwh
    else:
        self_sufficiency_ratio = 0

    return {
        "self_consumption_kwh": self_consumption_kwh,
        "total_consumption_kwh": total_consumption_kwh,
        "home_consumption_kwh": home_consumption_kwh,
        "self_sufficiency_ratio": self_sufficiency_ratio
    }
