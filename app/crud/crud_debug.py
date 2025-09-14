import random
from datetime import date, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from app.models import models

fake = Faker()

def fill_database_with_mock_data(db: Session):
    """
    Fill the database with mockup data for the last 2 years.
    """
    # Create one-time installations
    solar_panel = models.SolarPanel(
        name="Zonnepanelen Installatie",
        purchase_date=fake.date_between(start_date="-3y", end_date="today"),
        purchase_cost_eur=random.uniform(5000, 10000),
        total_power_wp=random.randint(3000, 6000),
        expected_annual_yield_kwh=random.randint(2500, 5500),
    )
    db.add(solar_panel)

    battery = models.Battery(
        name="Thuisbatterij",
        brand=fake.company(),
        purchase_date=fake.date_between(start_date="-3y", end_date="today"),
        purchase_cost_eur=random.uniform(3000, 8000),
        capacity_kwh=random.uniform(5, 15),
    )
    db.add(battery)

    car = models.Car(
        name=f"{fake.company()} {fake.license_plate()} {random.randint(1000, 9999)}",
        reimbursement_rate_eur_per_kwh=random.uniform(0.1, 0.3),
    )
    db.add(car)

    # Create tariffs
    today = date.today()
    tariffs = []
    for i in range(3):
        start_date = today - timedelta(days=(i + 1) * 365)
        end_date = today - timedelta(days=i * 365)
        tariff = models.Tariff(
            start_date=start_date,
            end_date=end_date,
            purchase_low_eur_kwh=random.uniform(0.1, 0.2),
            purchase_high_eur_kwh=random.uniform(0.2, 0.3),
            sale_eur_kwh=random.uniform(0.05, 0.15),
            vat_percentage=21.0,
            fixed_roi_rate_eur_kwh=random.uniform(0.05, 0.1),
        )
        db.add(tariff)
        tariffs.append(tariff)

    # Create monthly journal entries for the last 30 months
    current_year = today.year
    current_month = today.month
    for i in range(30):
        year = current_year
        month = current_month - i
        while month <= 0:
            month += 12
            year -= 1

        entry_date = date(year, month, 1)

        active_tariff = None
        for t in tariffs:
            if t.start_date <= entry_date and (t.end_date is None or t.end_date >= entry_date):
                active_tariff = t
                break

        journal_entry_data = {
            'year': year,
            'month': month,
            'grid_consumption_low_kwh': random.uniform(100, 300),
            'grid_consumption_high_kwh': random.uniform(50, 200),
            'grid_feed_in_low_kwh': random.uniform(20, 100),
            'grid_feed_in_high_kwh': random.uniform(10, 80),
            'solar_production_kwh': random.uniform(150, 400),
            'battery_charge_kwh': random.uniform(50, 150),
            'battery_discharge_kwh': random.uniform(40, 140),
            'monthly_prepayment_eur': random.uniform(80, 150),
        }

        if active_tariff:
            journal_entry_data['consumption_price_low_eur_kwh'] = active_tariff.purchase_low_eur_kwh
            journal_entry_data['consumption_price_high_eur_kwh'] = active_tariff.purchase_high_eur_kwh
            journal_entry_data['feed_in_tariff_low_eur_kwh'] = active_tariff.sale_eur_kwh
            journal_entry_data['feed_in_tariff_high_eur_kwh'] = active_tariff.sale_eur_kwh

        journal_entry = models.MonthlyJournal(
            **journal_entry_data
        )
        db.add(journal_entry)
        db.flush()

        car_journal_entry = models.CarJournalEntry(
            journal_id=journal_entry.id,
            car_id=car.id,
            total_charged_kwh=random.uniform(50, 200),
        )
        db.add(car_journal_entry)

    db.commit()
