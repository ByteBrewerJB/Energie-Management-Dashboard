from decimal import Decimal
from app.models import models
from app.schemas import journal as journal_schema

def calculate_monthly_statement(journal: models.MonthlyJournal) -> journal_schema.MonthlyStatement:
    """
    Calculates the complete financial statement for a given monthly journal.

    This single function handles all financial calculations, including energy costs,
    feed-in revenue, car reimbursements, and the final settlement.

    Args:
        journal: A MonthlyJournal database object containing all data for the month.

    Returns:
        A MonthlyStatement schema object with the calculated financial results.
    """
    # --- 1. Calculate Energy Costs & Revenue ---
    grid_consumption_low_kwh = Decimal(journal.grid_consumption_low_kwh)
    grid_consumption_high_kwh = Decimal(journal.grid_consumption_high_kwh)
    grid_feed_in_low_kwh = Decimal(journal.grid_feed_in_low_kwh)
    grid_feed_in_high_kwh = Decimal(journal.grid_feed_in_high_kwh)

    total_consumption_cost = (grid_consumption_low_kwh * journal.consumption_price_low_eur_kwh) + \
                             (grid_consumption_high_kwh * journal.consumption_price_high_eur_kwh)

    total_feed_in_revenue = (grid_feed_in_low_kwh * journal.feed_in_tariff_low_eur_kwh) + \
                              (grid_feed_in_high_kwh * journal.feed_in_tariff_high_eur_kwh)

    net_energy_cost = total_consumption_cost - total_feed_in_revenue

    # --- 2. Calculate Car Reimbursement ---
    total_car_reimbursement = Decimal(0)
    for entry in journal.car_entries:
        # The reimbursement rate is now on the Car model, accessed via the relationship
        rate = entry.car.reimbursement_rate_eur_per_kwh
        charged_kwh = Decimal(entry.total_charged_kwh)
        total_car_reimbursement += charged_kwh * rate

    # --- 3. Calculate Final Settlement ---
    # Final settlement = (What you get) - (What you paid)
    # What you get = feed-in revenue + car reimbursement
    # What you paid = consumption cost + monthly prepayment
    # Settlement = (total_feed_in_revenue + total_car_reimbursement) - (total_consumption_cost + journal.monthly_prepayment_eur)
    # Rearranging: (total_feed_in_revenue - total_consumption_cost) + total_car_reimbursement - monthly_prepayment_eur
    # Which is: -net_energy_cost + total_car_reimbursement - monthly_prepayment_eur

    final_settlement = total_car_reimbursement - net_energy_cost - journal.monthly_prepayment_eur

    # --- 4. Assemble the Statement ---
    statement = journal_schema.MonthlyStatement(
        total_consumption_cost_eur=total_consumption_cost,
        total_feed_in_revenue_eur=total_feed_in_revenue,
        net_energy_cost_eur=net_energy_cost,
        total_car_reimbursement_eur=total_car_reimbursement,
        final_settlement_eur=final_settlement,
    )

    return statement
