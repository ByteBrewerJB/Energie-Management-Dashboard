from calendar import month_abbr
from typing import Dict, List

from sqlalchemy.orm import Session

from ..models.assets import SolarPanelInstallation
from ..models.monthly_journal import MonthlyJournal
from ..schemas.dashboard import (
    ConsumptionSplitEntry,
    DashboardResponse,
    EnergyBalanceEntry,
    MonthlyFinancials,
    MonthlyKPI,
    ProductionComparisonEntry,
)


def _month_label(month: int) -> str:
    label = month_abbr[month]
    return label or str(month)


def _safe(value: float | None) -> float:
    return float(value) if value is not None else 0.0


def get_dashboard_data(db: Session, owner_id: int, year: int) -> DashboardResponse:
    journals = (
        db.query(MonthlyJournal)
        .filter(MonthlyJournal.owner_id == owner_id, MonthlyJournal.year == year)
        .order_by(MonthlyJournal.month.asc())
        .all()
    )
    journals_by_month: Dict[int, MonthlyJournal] = {j.month: j for j in journals}

    solar_installation = (
        db.query(SolarPanelInstallation)
        .filter(SolarPanelInstallation.owner_id == owner_id)
        .first()
    )
    expected_yearly_production = _safe(
        solar_installation.expected_annual_yield_kwh if solar_installation else None
    )
    expected_monthly_production = expected_yearly_production / 12 if expected_yearly_production else 0.0

    kpi_items: List[MonthlyKPI] = []
    financial_items: List[MonthlyFinancials] = []
    energy_balance_items: List[EnergyBalanceEntry] = []
    consumption_split_items: List[ConsumptionSplitEntry] = []
    production_items: List[ProductionComparisonEntry] = []

    for month in range(1, 13):
        journal = journals_by_month.get(month)

        cons_tariff_1 = _safe(journal.consumption_tariff_1_kwh if journal else None)
        cons_tariff_2 = _safe(journal.consumption_tariff_2_kwh if journal else None)
        tariff_low = _safe(journal.avg_consumption_tariff_low_eur_kwh if journal else None)
        tariff_high = _safe(journal.avg_consumption_tariff_high_eur_kwh if journal else None)
        total_consumption = _safe(journal.total_house_consumption_kwh if journal else None)
        solar_production = _safe(journal.solar_production_kwh if journal else None)
        feed_in_kwh = _safe(journal.feed_in_without_battery_kwh if journal else None)
        feed_in_tariff = _safe(journal.avg_feed_in_tariff_eur_kwh if journal else None)
        supplier_costs = _safe(journal.supplier_costs_eur if journal else None)
        advance_payment = _safe(journal.advance_payment_eur if journal else None)

        consumption_costs = cons_tariff_1 * tariff_low + cons_tariff_2 * tariff_high
        purchased_kwh = cons_tariff_1 + cons_tariff_2
        effective_rate = (consumption_costs / purchased_kwh) if purchased_kwh else (tariff_low + tariff_high) / 2

        ev_consumption = 0.0
        car_reimbursement = 0.0
        if journal:
            for charge in journal.car_charges:
                charged_kwh = _safe(charge.charged_kwh)
                ev_consumption += charged_kwh
                rate = _safe(
                    charge.car.reimbursement_rate_inc_vat_eur_kwh if charge.car else None
                )
                car_reimbursement += charged_kwh * rate

        household_consumption = max(total_consumption - ev_consumption, 0.0)

        self_consumption = min(total_consumption, solar_production)
        net_import = max(total_consumption - self_consumption, 0.0)
        net_export = feed_in_kwh if feed_in_kwh else max(solar_production - self_consumption, 0.0)
        feed_in_revenue = feed_in_kwh * feed_in_tariff
        self_consumption_value = self_consumption * effective_rate
        savings = self_consumption_value + feed_in_revenue + car_reimbursement
        net_balance = savings - consumption_costs
        self_sufficiency_pct = (self_consumption / total_consumption * 100) if total_consumption else 0.0
        net_energy_costs = supplier_costs if supplier_costs else consumption_costs - feed_in_revenue
        final_settlement = net_energy_costs - advance_payment - car_reimbursement - feed_in_revenue

        kpi_items.append(
            MonthlyKPI(
                month=month,
                month_label=_month_label(month),
                net_balance_eur=round(net_balance, 2),
                self_sufficiency_pct=round(self_sufficiency_pct, 2),
                total_production_kwh=round(solar_production, 2),
                total_consumption_kwh=round(total_consumption, 2),
                savings_eur=round(savings, 2),
            )
        )
        financial_items.append(
            MonthlyFinancials(
                month=month,
                consumption_costs_eur=round(consumption_costs, 2),
                feed_in_revenue_eur=round(feed_in_revenue, 2),
                net_energy_costs_eur=round(net_energy_costs, 2),
                advance_payment_eur=round(advance_payment, 2),
                car_reimbursement_eur=round(car_reimbursement, 2),
                final_settlement_eur=round(final_settlement, 2),
            )
        )
        energy_balance_items.append(
            EnergyBalanceEntry(
                month=month,
                net_import_kwh=round(net_import, 2),
                self_consumption_kwh=round(self_consumption, 2),
                net_export_kwh=round(net_export, 2),
            )
        )
        consumption_split_items.append(
            ConsumptionSplitEntry(
                month=month,
                household_kwh=round(household_consumption, 2),
                ev_kwh=round(ev_consumption, 2),
            )
        )
        production_items.append(
            ProductionComparisonEntry(
                month=month,
                actual_production_kwh=round(solar_production, 2),
                expected_production_kwh=round(expected_monthly_production, 2),
            )
        )

    return DashboardResponse(
        year=year,
        kpis=kpi_items,
        financials=financial_items,
        energy_balance=energy_balance_items,
        consumption_split=consumption_split_items,
        production_vs_expectation=production_items,
    )
