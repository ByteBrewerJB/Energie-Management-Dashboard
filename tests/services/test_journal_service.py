import pytest
from sqlalchemy.orm import Session
from app.services import journal_service
from app.models.journal import MonthlyJournal
from app.models.car import Car
from app.models.entity import Entity
from app.models.journal import CarJournalEntry

def test_process_journal_entry(db: Session):
    """
    Tests the journal processing service logic in isolation.
    The `db` fixture from conftest provides a clean, isolated database session.
    """
    # 1. Create mock data in the test DB
    test_car = Car(id=1, name="Test EV", reimbursement_rate_eur_per_kwh=0.20)
    test_entity = Entity(id=1, name="Test Entity")

    test_journal = MonthlyJournal(
        id=1,
        year=2023,
        month=1,
        grid_consumption_low_kwh=100,
        grid_consumption_high_kwh=50,
        grid_feed_in_low_kwh=20,
        grid_feed_in_high_kwh=10,
        consumption_price_low_eur_kwh=0.30,
        consumption_price_high_eur_kwh=0.40,
        feed_in_tariff_low_eur_kwh=0.10,
        feed_in_tariff_high_eur_kwh=0.08,
        solar_production_kwh=200,
        battery_charge_kwh=50,
        battery_discharge_kwh=40,
        monthly_prepayment_eur=100,
    )
    db.add(test_car)
    db.add(test_entity)
    db.add(test_journal)
    db.commit()

    test_car_entry = CarJournalEntry(
        id=1,
        total_charged_kwh=100,
        monthly_journal_id=test_journal.id,
        car_id=test_car.id,
        entity_id=test_entity.id,
    )
    db.add(test_car_entry)
    db.commit()

    db.refresh(test_journal)

    # 2. Process the data
    processed_data = journal_service.process_journal_entry(db, test_journal)

    # 3. Assert calculations
    assert processed_data.total_consumption_cost_excl_vat == 50.0
    assert processed_data.total_feed_in_revenue == 2.8
    assert processed_data.total_car_reimbursement_eur == 20.0
    assert processed_data.net_balance == pytest.approx(-137.7)
    assert processed_data.self_consumption_kwh == 170
    assert processed_data.total_consumption_kwh == 360
    assert processed_data.self_sufficiency_pct == pytest.approx(58.33, rel=1e-2)
