from sqlalchemy.orm import Session

from ..models.assets import Battery, SolarPanelInstallation
from ..models.monthly_journal import MonthlyJournal
from ..schemas.dashboard import ROIProgress
from .dashboard import _safe


def calculate_roi(db: Session, owner_id: int) -> ROIProgress:
    solar = db.query(SolarPanelInstallation).filter(SolarPanelInstallation.owner_id == owner_id).first()
    battery = db.query(Battery).filter(Battery.owner_id == owner_id).first()

    total_investment = _safe(solar.purchase_cost_eur if solar else None) + _safe(
        battery.purchase_cost_eur if battery else None
    )

    journals = db.query(MonthlyJournal).filter(MonthlyJournal.owner_id == owner_id).all()

    total_savings = 0.0
    for journal in journals:
        cons_tariff_1 = _safe(journal.consumption_tariff_1_kwh)
        cons_tariff_2 = _safe(journal.consumption_tariff_2_kwh)
        tariff_low = _safe(journal.avg_consumption_tariff_low_eur_kwh)
        tariff_high = _safe(journal.avg_consumption_tariff_high_eur_kwh)
        total_consumption = _safe(journal.total_house_consumption_kwh)
        solar_production = _safe(journal.solar_production_kwh)
        feed_in_kwh = _safe(journal.feed_in_without_battery_kwh)
        feed_in_tariff = _safe(journal.avg_feed_in_tariff_eur_kwh)

        consumption_costs = cons_tariff_1 * tariff_low + cons_tariff_2 * tariff_high
        purchased_kwh = cons_tariff_1 + cons_tariff_2
        effective_rate = (consumption_costs / purchased_kwh) if purchased_kwh else (tariff_low + tariff_high) / 2

        self_consumption = min(total_consumption, solar_production)
        feed_in_revenue = feed_in_kwh * feed_in_tariff
        self_consumption_value = self_consumption * effective_rate

        car_reimbursement = 0.0
        for charge in journal.car_charges:
            rate = _safe(charge.car.reimbursement_rate_inc_vat_eur_kwh if charge.car else None)
            car_reimbursement += _safe(charge.charged_kwh) * rate

        total_savings += self_consumption_value + feed_in_revenue + car_reimbursement

    progress_ratio = (total_savings / total_investment) if total_investment else 0.0

    return ROIProgress(
        total_investment_eur=round(total_investment, 2),
        total_savings_eur=round(total_savings, 2),
        progress_ratio=round(progress_ratio, 4),
    )
