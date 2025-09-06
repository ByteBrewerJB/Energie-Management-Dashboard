import pandas as pd
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud import crud_investments, crud_tariffs, crud_metrics
from app.schemas.investment import InvestmentCreate
from app.schemas.tariff import TariffCreate
from app.schemas.metrics import MonthlyMetricCreate
from datetime import date

from app.models import models

def seed_db():
    db: Session = SessionLocal()

    # Seed Investments
    if db.query(models.Investment).count() == 0:
        investment_df = pd.read_csv('scripts/data/investment.csv', parse_dates=['install_date'])
        investment_data = investment_df.iloc[0].to_dict()
        investment = InvestmentCreate(
            description=investment_data['description'],
            installation_date=investment_data['install_date'],
            total_cost_eur=investment_data['total_investment_cost'],
            total_power_wp=investment_data['total_wp'],
            estimated_annual_production_kwh=investment_data['estimated_annual_production_kwh']
        )
        crud_investments.create_investment(db, investment=investment)
        print("✅ Investment seeded.")
    else:
        print("ℹ️ Investments already exist, skipping.")

    # Seed Tariffs
    tariffs_df = pd.read_csv('scripts/data/tariffs.csv', parse_dates=['start_date', 'end_date'])
    for _, row in tariffs_df.iterrows():
        row_data = row.to_dict()
        if pd.isna(row_data.get('end_date')):
            row_data['end_date'] = None

        tariff = TariffCreate(
            start_date=row_data['start_date'],
            end_date=row_data['end_date'],
            purchase_low_eur_kwh=row_data['purchase_rate_low'],
            purchase_high_eur_kwh=row_data['purchase_rate_high'],
            sale_eur_kwh=row_data['feed_in_rate'],
            vat_percentage=row_data['vat_percentage'] / 100,
            fixed_roi_rate_eur_kwh=row_data['fixed_roi_rate']
        )

        exists = db.query(models.Tariff).filter(models.Tariff.start_date == tariff.start_date).first()
        if not exists:
            crud_tariffs.create_tariff(db, tariff=tariff)
            print(f"✅ Tariff for {tariff.start_date.date()} seeded.")
        else:
            print(f"ℹ️ Tariff for {tariff.start_date.date()} already exists, skipping.")

    # Seed Metrics
    metrics_df = pd.read_csv('scripts/data/metrics.csv', parse_dates=['period'])
    for _, row in metrics_df.iterrows():
        metric = MonthlyMetricCreate(
            period_start=row['period'],
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

        exists = db.query(models.MonthlyMetric).filter(models.MonthlyMetric.period_start == metric.period_start).first()
        if not exists:
            crud_metrics.create_monthly_metric(db, metric=metric)
            print(f"✅ Metric for {metric.period_start.date()} seeded.")
        else:
            print(f"ℹ️ Metric for {metric.period_start.date()} already exists, skipping.")

    db.close()
    print("\nDatabase seeding check complete! 🌱")

if __name__ == "__main__":
    seed_db()
