from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Any
from app.models.models import MonthlyEnergy, SolarInvestmentOption

def to_decimal(value, default='0.0') -> Decimal:
    """Safely convert a value to a Decimal."""
    if value is None:
        value = default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return Decimal(default)

def calculate_monthly_metrics(record: MonthlyEnergy) -> Dict[str, Any]:
    """
    Calculates all computed fields for a MonthlyEnergy record using Decimal for precision.
    """
    if not record:
        return {}

    # --- Convert all inputs to Decimal for consistent calculations ---
    house_low_kwh = to_decimal(record.house_low_kwh)
    house_high_kwh = to_decimal(record.house_high_kwh)
    pv_production_kwh = to_decimal(record.pv_production_kwh)
    pv_backfeed_kwh = to_decimal(record.pv_backfeed_kwh)
    ev_kwh = to_decimal(record.ev_kwh)
    auto_eur = to_decimal(record.auto_eur)
    feedin_rate = to_decimal(record.feedin_rate_eur_per_kwh)
    billed_kwh = to_decimal(record.billed_kwh, default=None)
    energy_unit_price = to_decimal(record.energy_unit_price_eur, default=None)
    vat_rate = to_decimal(record.vat_rate, default='0.21')

    # --- Calculations ---
    house_kwh_total = house_low_kwh + house_high_kwh
    pv_self_consumption_kwh = max(Decimal(0), pv_production_kwh - pv_backfeed_kwh)
    pv_revenue_eur = pv_backfeed_kwh * feedin_rate
    total_consumption_kwh = house_kwh_total + ev_kwh

    self_consumption_ratio = pv_self_consumption_kwh / max(pv_production_kwh, Decimal(1))
    pv_coverage_ratio = pv_self_consumption_kwh / max(total_consumption_kwh, Decimal(1))

    auto_effective_eur_per_kwh = None
    if ev_kwh > Decimal(0):
        auto_effective_eur_per_kwh = auto_eur / ev_kwh

    billed_total_excl_vat_eur = None
    if billed_kwh is not None and energy_unit_price is not None:
        billed_total_excl_vat_eur = billed_kwh * energy_unit_price

    billed_total_incl_vat_eur = None
    if billed_total_excl_vat_eur is not None:
        billed_total_incl_vat_eur = billed_total_excl_vat_eur * (Decimal(1) + vat_rate)

    return {
        "house_kwh_total": float(house_kwh_total),
        "pv_self_consumption_kwh": float(pv_self_consumption_kwh),
        "pv_revenue_eur": custom_round(pv_revenue_eur, 2),
        "total_consumption_kwh": float(total_consumption_kwh),
        "self_consumption_ratio": float(custom_round(self_consumption_ratio, 4)),
        "pv_coverage_ratio": float(custom_round(pv_coverage_ratio, 4)),
        "auto_effective_eur_per_kwh": custom_round(auto_effective_eur_per_kwh, 4),
        "billed_total_excl_vat_eur": custom_round(billed_total_excl_vat_eur, 2),
        "billed_total_incl_vat_eur": custom_round(billed_total_incl_vat_eur, 2),
    }

def calculate_investment_metrics(investment: SolarInvestmentOption) -> Dict[str, Any]:
    """
    Calculates all computed fields for a SolarInvestmentOption record.
    """
    if not investment:
        return {}

    total_cost = to_decimal(investment.total_cost_eur)
    panels = to_decimal(investment.panels, default='1')
    annual_production = to_decimal(investment.annual_production_kwh)
    assumed_price = to_decimal(investment.assumed_energy_price_eur_per_kwh, default='0.40')

    # --- Calculations ---
    price_per_panel_eur = None
    if panels > Decimal(0):
        price_per_panel_eur = total_cost / panels

    savings_first_year_eur = annual_production * assumed_price

    payback_years = None
    if savings_first_year_eur > Decimal('0.01'):
        payback_years = total_cost / savings_first_year_eur

    return {
        "price_per_panel_eur": custom_round(price_per_panel_eur, 2),
        "savings_first_year_eur": custom_round(savings_first_year_eur, 2),
        "payback_years": custom_round(payback_years, 2),
    }

def custom_round(d: Decimal, decimals: int):
    """
    Custom round function to handle None and use ROUND_HALF_UP.
    """
    if d is None:
        return None
    quantizer = Decimal('1e-' + str(decimals))
    return d.quantize(quantizer, rounding=ROUND_HALF_UP)
