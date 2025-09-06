import os
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

# Adjust the path to import from the parent directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.models import Base, Investment, Tariff, MonthlyMetric
from app.db.session import SessionLocal, engine

def import_investments(db: Session, filepath: str):
    print("Importing investments...")
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        investment = Investment(
            description=row['description'],
            installation_date=datetime.strptime(row['install_date'], '%Y-%m-%d').date(),
            total_cost_eur=row['total_investment_cost'],
            total_power_wp=row['total_wp'],
            estimated_annual_production_kwh=row['estimated_annual_production_kwh']
        )
        db.add(investment)
    print("Investments imported successfully.")

def import_tariffs(db: Session, filepath: str):
    print("Importing tariffs...")
    df = pd.read_csv(filepath, parse_dates=['start_date', 'end_date'])
    for _, row in df.iterrows():
        # Pandas converts empty date fields to NaT (Not a Time)
        end_date = row['end_date'].date() if pd.notna(row['end_date']) else None

        tariff = Tariff(
            start_date=row['start_date'].date(),
            end_date=end_date,
            purchase_low_eur_kwh=row['purchase_rate_low'],
            purchase_high_eur_kwh=row['purchase_rate_high'],
            sale_eur_kwh=row['feed_in_rate'],
            vat_percentage=row['vat_percentage'],
            fixed_roi_rate_eur_kwh=row['fixed_roi_rate']
        )
        db.add(tariff)
    print("Tariffs imported successfully.")

def import_metrics(db: Session, filepath: str):
    print("Importing monthly metrics...")
    df = pd.read_csv(filepath, parse_dates=['period'])
    for _, row in df.iterrows():
        metric = MonthlyMetric(
            period_start=row['period'].date(),
            account_name=row['account'],
            production_total_kwh=row['total_generated_kwh'],
            import_low_kwh=row['import_low_rate_kwh'],
            import_high_kwh=row['import_high_rate_kwh'],
            export_total_kwh=row['total_feed_in_kwh'],
            consumption_ev_kwh=row['ev_consumption_kwh'],
            battery_charge_kwh=row['battery_charge_kwh'],
            battery_discharge_kwh=row['battery_discharge_kwh'],
            monthly_prepayment_eur=row['prepayment_amount']
        )
        db.add(metric)
    print("Monthly metrics imported successfully.")

def main():
    print("Starting initial data import...")

    # In a real scenario, we would use Alembic to create tables.
    # For this script, we assume tables already exist.
    # Base.metadata.create_all(bind=engine) # This should be handled by migrations

    db = SessionLocal()

    try:
        # Define file paths relative to this script's location
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        import_investments(db, os.path.join(data_dir, 'investment.csv'))
        import_tariffs(db, os.path.join(data_dir, 'tariffs.csv'))
        import_metrics(db, os.path.join(data_dir, 'metrics.csv'))

        db.commit()
        print("\nData import complete. All data has been committed to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Rolling back changes.")
        db.rollback()
    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    # This script is intended to be run from the command line in an environment
    # where the database is accessible.
    # Example: docker-compose exec backend python scripts/import_data.py
    print("NOTE: This script will fail if the database is not accessible or if tables are not created.")
    # Due to environment limitations, we cannot run main() here.
    # main()
