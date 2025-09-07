from typing import List
from app.models.models import MonthlyMetric, Tariff, CarUsage
from decimal import Decimal

def calculate_energy_financials(metric: MonthlyMetric, tariff: Tariff) -> dict:
    """
    Calculates financial values for energy consumption and production based on a
    MonthlyMetric and a monthly Tariff.

    Args:
        metric: A MonthlyMetric object for a specific month.
        tariff: A Tariff object for the same month.

    Returns:
        A dictionary with the calculated financial values for energy.
    """
    # Ensure all inputs are treated as Decimal for precision
    grid_consumption_low_kwh = Decimal(metric.grid_consumption_low_kwh or 0)
    grid_consumption_high_kwh = Decimal(metric.grid_consumption_high_kwh or 0)
    grid_feed_in_low_kwh = Decimal(metric.grid_feed_in_low_kwh or 0)
    grid_feed_in_high_kwh = Decimal(metric.grid_feed_in_high_kwh or 0)

    # Calculate total cost of energy purchased from the grid (excluding VAT)
    total_consumption_cost = (grid_consumption_low_kwh * tariff.consumption_price_low_eur_kwh) + \
                             (grid_consumption_high_kwh * tariff.consumption_price_high_eur_kwh)

    # Calculate total revenue from energy sold to the grid (excluding VAT)
    total_feed_in_revenue = (grid_feed_in_low_kwh * tariff.feed_in_tariff_low_eur_kwh) + \
                              (grid_feed_in_high_kwh * tariff.feed_in_tariff_high_eur_kwh)

    net_energy_result = total_feed_in_revenue - total_consumption_cost

    vat_multiplier = Decimal(1) + tariff.vat_percentage

    return {
        "total_consumption_cost_eur": total_consumption_cost,
        "total_feed_in_revenue_eur": total_feed_in_revenue,
        "net_energy_result_eur": net_energy_result,
        "total_consumption_cost_inc_vat_eur": total_consumption_cost * vat_multiplier,
        "total_feed_in_revenue_inc_vat_eur": total_feed_in_revenue * vat_multiplier,
        "net_energy_result_inc_vat_eur": net_energy_result * vat_multiplier,
    }

def calculate_car_reimbursement(car_usage_records: List[CarUsage]) -> Decimal:
    """
    Calculates the total reimbursed amount for car charging for a specific month.

    Args:
        car_usage_records: A list of CarUsage objects for the month.

    Returns:
        The total declarable amount in Euros.
    """
    total_reimbursement = Decimal(0)
    for record in car_usage_records:
        total_reimbursement += Decimal(record.total_charged_kwh) * record.reimbursement_rate_eur_per_kwh
    return total_reimbursement

def calculate_monthly_settlement(
    net_energy_result_inc_vat: Decimal,
    car_reimbursement_eur: Decimal,
    monthly_prepayment_eur: Decimal
) -> Decimal:
    """
    Calculates the final monthly settlement (Eindafrekening Maand).

    This function settles the net energy costs, car reimbursements, and the
    monthly prepayment.

    Args:
        net_energy_result_inc_vat: The net result from energy costs/revenue (incl. VAT).
        car_reimbursement_eur: The total reimbursement for car charging.
        monthly_prepayment_eur: The monthly advance payment made to the energy supplier.

    Returns:
        The final settlement amount in Euros. A positive value means a refund
        is due, a negative value means an additional payment is required.
    """
    # The settlement is the sum of revenues minus the costs.
    # Revenues: feed-in revenue, car reimbursement.
    # Costs: consumption cost, prepayment.
    # Using the pre-calculated net_energy_result which is (feed-in - consumption)
    # The monthly_prepayment is a cost already paid, so it reduces the final bill.
    # A positive result from (net_energy + car_reimbursement) means you earned money.
    # From this, you subtract the prepayment.
    # Let's define it as: (What you get back) - (What you owe)
    # Final settlement = (car_reimbursement) - (net_energy_cost) - (prepayment)
    # where net_energy_cost is (consumption - feed-in).
    # so net_energy_result is (feed-in - consumption) = -net_energy_cost
    # Final settlement = car_reimbursement + net_energy_result - prepayment

    final_settlement = car_reimbursement_eur + net_energy_result_inc_vat - monthly_prepayment_eur
    return final_settlement
