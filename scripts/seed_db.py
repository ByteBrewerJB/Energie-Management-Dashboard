import pandas as pd
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud import crud_investments, crud_tariffs, crud_metrics
from app.schemas.investment import InvestmentCreate
from app.schemas.tariff import TariffCreate
from app.schemas.metrics import MonthlyMetricCreate
from datetime import date

def seed_db():
    db: Session = SessionLocal()

    # Seed Investments
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
            vat_percentage=row_data['vat_percentage'] / 100, # Convert percentage to float
            fixed_roi_rate_eur_kwh=row_data['fixed_roi_rate']
        )
        crud_tariffs.create_tariff(db, tariff=tariff)

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
        crud_metrics.create_monthly_metric(db, metric=metric)

    db.close()
    print("Database has been seeded successfully!")

if __name__ == "__main__":
    seed_db()
