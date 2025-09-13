from sqlalchemy.orm import Session
from app.models.journal import MonthlyJournal as MonthlyJournalModel
from app.schemas.journal import MonthlyJournal as MonthlyJournalSchema
from app import crud

def process_journal_entry(db: Session, journal_entry: MonthlyJournalModel) -> MonthlyJournalSchema:
    """
    Takes a raw MonthlyJournal entry from the DB and returns a fully processed
    schema with all calculated fields.
    """

    # --- Financial Calculations ---

    # 1. Total Consumption Cost
    cost_low = journal_entry.grid_consumption_low_kwh * journal_entry.consumption_price_low_eur_kwh
    cost_high = journal_entry.grid_consumption_high_kwh * journal_entry.consumption_price_high_eur_kwh
    total_consumption_cost_excl_vat = cost_low + cost_high

    # Assuming VAT is stored as a decimal, e.g., 0.21 for 21%
    # The spec is ambiguous here, but this is a reasonable assumption.
    # I will assume there is a tariff associated with the journal month to get the VAT.
    # For now, I'll hardcode it, and will need to refactor this later when tariff logic is integrated.
    vat_rate = 0.21 # Placeholder
    total_consumption_cost_incl_vat = total_consumption_cost_excl_vat * (1 + vat_rate)

    # 2. Total Feed-in Revenue
    revenue_low = journal_entry.grid_feed_in_low_kwh * journal_entry.feed_in_tariff_low_eur_kwh
    revenue_high = journal_entry.grid_feed_in_high_kwh * journal_entry.feed_in_tariff_high_eur_kwh
    total_feed_in_revenue = revenue_low + revenue_high

    # 3. Total Car Reimbursement
    total_car_reimbursement_eur = 0
    for car_entry in journal_entry.car_journal_entries:
        car = crud.car.get_car(db, car_id=car_entry.car_id)
        if car:
            total_car_reimbursement_eur += car_entry.total_charged_kwh * car.reimbursement_rate_eur_per_kwh

    # 4. Net Balance ("Naar eigen rekening")
    net_balance = (total_feed_in_revenue + total_car_reimbursement_eur) - total_consumption_cost_incl_vat - journal_entry.monthly_prepayment_eur


    # --- Energy Flow Calculations ---

    # Total consumption is what the home used, regardless of source
    # Home Consumption = Solar used by home + Battery used by home + Grid consumption
    # Solar used by home = Solar Production - Grid Feed-in
    # This assumes excess solar is always fed to the grid, which is a simplification.
    # A better model would be: Home Consumption = (Solar Production - Grid Feed-in) + (Battery Discharge - Battery Charge from Grid) + Grid Consumption
    # The spec is not super detailed here, so I will use a reasonable interpretation.
    # Self-consumption = what you used from your own solar panels.
    # Self-consumption = Solar Production - Grid Feed-in
    self_consumption_kwh = journal_entry.solar_production_kwh - (journal_entry.grid_feed_in_low_kwh + journal_entry.grid_feed_in_high_kwh)

    total_grid_consumption = journal_entry.grid_consumption_low_kwh + journal_entry.grid_consumption_high_kwh
    total_consumption_kwh = self_consumption_kwh + journal_entry.battery_discharge_kwh + total_grid_consumption

    # Self-sufficiency = how much of your total consumption was met by your own sources (solar + battery)
    if total_consumption_kwh > 0:
        self_sufficiency_pct = ((self_consumption_kwh + journal_entry.battery_discharge_kwh) / total_consumption_kwh) * 100
    else:
        self_sufficiency_pct = 0.0


    # --- Construct the final response schema ---

    processed_data = MonthlyJournalSchema(
        **journal_entry.__dict__,
        total_consumption_cost_excl_vat=total_consumption_cost_excl_vat,
        total_consumption_cost_incl_vat=total_consumption_cost_incl_vat,
        total_feed_in_revenue=total_feed_in_revenue,
        total_car_reimbursement_eur=total_car_reimbursement_eur,
        net_balance=net_balance,
        self_consumption_kwh=self_consumption_kwh,
        self_sufficiency_pct=self_sufficiency_pct,
        total_consumption_kwh=total_consumption_kwh,
    )

    return processed_data
