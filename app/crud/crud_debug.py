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
        purchase_date=fake.date_between(start_date="-3y", end_date="today"),
        purchase_cost_eur=random.uniform(5000, 10000),
        total_power_wp=random.randint(3000, 6000),
        expected_annual_yield_kwh=random.randint(2500, 5500),
    )
    db.add(solar_panel)

    battery = models.Battery(
        purchase_date=fake.date_between(start_date="-3y", end_date="today"),
        purchase_cost_eur=random.uniform(3000, 8000),
        capacity_kwh=random.uniform(5, 15),
    )
    db.add(battery)

    car = models.Car(
        name=fake.company() + " " + fake.license_plate(),
        reimbursement_rate_eur_per_kwh=random.uniform(0.1, 0.3),
    )
    db.add(car)

    # Create tariffs
    today = date.today()
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
        )
        db.add(tariff)

    # Create monthly journal entries for the last 24 months
    current_year = today.year
    current_month = today.month
    for i in range(24):
        year = current_year
        month = current_month - i
        while month <= 0:
            month += 12
            year -= 1

        journal_entry = models.MonthlyJournal(
            year=year,
            month=month,
            grid_consumption_low_kwh=random.uniform(100, 300),
            grid_consumption_high_kwh=random.uniform(50, 200),
            grid_feed_in_low_kwh=random.uniform(20, 100),
            grid_feed_in_high_kwh=random.uniform(10, 80),
            solar_production_kwh=random.uniform(150, 400),
            battery_charge_kwh=random.uniform(50, 150),
            battery_discharge_kwh=random.uniform(40, 140),
            monthly_prepayment_eur=random.uniform(80, 150),
        )
        db.add(journal_entry)
        db.flush()  # Flush to get the journal_entry.id

        car_journal_entry = models.CarJournalEntry(
            journal_id=journal_entry.id,
            car_id=car.id,
            total_charged_kwh=random.uniform(50, 200),
        )
        db.add(car_journal_entry)

    db.commit()
