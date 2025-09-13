import pytest
from sqlalchemy.orm import Session
from app.services import roi_service
from app.models.solar_panel import SolarPanel
from app.models.battery import Battery
from app.models.journal import MonthlyJournal

def test_get_solar_panel_roi(db: Session):
    # 1. Create mock data
    test_panel = SolarPanel(id=1, name="Test Panels", purchase_cost_eur=10000, power_capacity_kwp=5)
    test_journal = MonthlyJournal(
        year=2023, month=1,
        grid_feed_in_low_kwh=100, feed_in_tariff_low_eur_kwh=0.10, # Revenue = 10
        solar_production_kwh=300,
        consumption_price_low_eur_kwh=0.30, consumption_price_high_eur_kwh=0.50 # Avg = 0.40
    )
    # Self-consumption = 300 - 100 = 200 kWh. Avoided cost = 200 * 0.40 = 80
    db.add(test_panel)
    db.add(test_journal)
    db.commit()

    # 2. Process the data
    roi_data = roi_service.get_solar_panel_roi(db, solar_panel_id=1)

    # 3. Assert calculations
    assert roi_data is not None
    assert roi_data.total_investment == 10000
    assert roi_data.monthly_breakdown[0].revenue == 10.0
    assert roi_data.monthly_breakdown[0].avoided_cost == 80.0
    assert roi_data.total_savings == 90.0
    # ROI = 90 / 10000 * 100 = 0.9%
    assert roi_data.roi_percentage == pytest.approx(0.9)


def test_get_battery_roi(db: Session):
    # 1. Create mock data
    test_battery = Battery(id=1, name="Test Battery", purchase_cost_eur=5000, capacity_kwh=10)
    test_journal = MonthlyJournal(
        year=2023, month=1,
        battery_discharge_kwh=100,
        consumption_price_high_eur_kwh=0.50 # Avoided cost = 100 * 0.50 = 50
    )
    db.add(test_battery)
    db.add(test_journal)
    db.commit()

    # 2. Process the data
    roi_data = roi_service.get_battery_roi(db, battery_id=1)

    # 3. Assert calculations
    assert roi_data is not None
    assert roi_data.total_investment == 5000
    assert roi_data.total_savings == 50.0
    # ROI = 50 / 5000 * 100 = 1.0%
    assert roi_data.roi_percentage == pytest.approx(1.0)
