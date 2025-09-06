import json
import uuid
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.models import Base, MonthlyEnergy, SolarInvestmentOption

DATABASE_URL = "sqlite:////app/joulejournal.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The historical data provided by the user
HISTORY_DATA = {
    "monthly_energy_history": [
        { "year": 2025, "month": "Jan", "pv_production_kwh": 91.03, "pv_backfeed_kwh": 21.2, "pv_self_consumption_kwh": 69.83, "ev_kwh": 866.75, "auto_eur": 327.016194175, "auto_effective_eur_per_kwh": 0.3773, "house_low_kwh": 658.02, "house_high_kwh": 727.69, "low_tariff_eur_per_kwh": 0.26425, "high_tariff_eur_per_kwh": 0.26425, "feedin_rate_eur_per_kwh": 0.26425, "pv_revenue_eur": 5.6021, "battery_charge_kwh": 0, "battery_discharge_kwh": 0, "total_consumption_kwh": 1460.0, "house_consumption_kwh": 1385.71, "ev_consumption_kwh_total": 518.96, "self_use_kwh": 593.25, "advance_payment_eur": 0, "settlement_to_own_account_eur": 0, "billed_kwh": 524.06, "energy_unit_price_eur": 0.31181, "billed_total_excl_vat_eur": 163.41, "billed_total_incl_vat_eur": 197.72 },
        { "year": 2025, "month": "Apr", "pv_production_kwh": 882.72, "pv_backfeed_kwh": 588.0, "pv_self_consumption_kwh": 294.72, "ev_kwh": 690.63, "auto_eur": 260.567862, "auto_effective_eur_per_kwh": 0.3773, "house_low_kwh": 255.2, "house_high_kwh": 633.31, "low_tariff_eur_per_kwh": 0.26425, "high_tariff_eur_per_kwh": 0.26425, "feedin_rate_eur_per_kwh": 0.26425, "pv_revenue_eur": 155.379, "battery_charge_kwh": 0, "battery_discharge_kwh": 0, "total_consumption_kwh": 1180.0, "house_consumption_kwh": 888.51, "ev_consumption_kwh_total": 197.88, "self_use_kwh": 489.37, "advance_payment_eur": 0, "settlement_to_own_account_eur": 0, "billed_kwh": 342.71, "energy_unit_price_eur": 0.31181, "billed_total_excl_vat_eur": 106.86, "billed_total_incl_vat_eur": 129.30 },
        { "year": 2025, "month": "Aug", "pv_production_kwh": 881.7, "pv_backfeed_kwh": 903.2, "pv_self_consumption_kwh": -21.5, "ev_kwh": 264.5, "auto_eur": 222.21323145, "auto_effective_eur_per_kwh": 0.8401, "house_low_kwh": 621.07, "house_high_kwh": 602.84, "low_tariff_eur_per_kwh": 0.23, "high_tariff_eur_per_kwh": 0.23, "feedin_rate_eur_per_kwh": 0.19, "pv_revenue_eur": 171.608, "battery_charge_kwh": 790.9, "battery_discharge_kwh": 670.08, "total_consumption_kwh": 1080.0, "house_consumption_kwh": 1223.91, "ev_consumption_kwh_total": 959.41, "self_use_kwh": 815.5, "advance_payment_eur": 224.92, "settlement_to_own_account_eur": -175.08, "billed_kwh": 212.86, "energy_unit_price_eur": 0.31181, "billed_total_excl_vat_eur": 66.37, "billed_total_incl_vat_eur": 202.73 }
    ],
    "solar_investment_options": [
        { "supplier": "DoWatt 17 Normal", "panels": 17, "panel_type": "JA Solar 435W N-type TOPCon Bifacial", "total_power_wp": 7395, "annual_production_kwh": 7232, "inverter": "Growatt MIN 6000 TL-XH", "assumed_energy_price_eur_per_kwh": 0.40, "total_cost_eur": 7000.00 },
        { "supplier": "18 DoWatt 2", "panels": 18, "panel_type": "JA Solar 435W", "total_power_wp": 7830, "annual_production_kwh": 7489, "inverter": "Enphase IQ8+ Micro Omvormers", "assumed_energy_price_eur_per_kwh": 0.40, "total_cost_eur": 8499.00 }
    ]
}

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding monthly energy data...")
        for record in HISTORY_DATA["monthly_energy_history"]:
            # Check if record already exists
            exists = db.query(MonthlyEnergy).filter_by(
                year=record["year"],
                month=MONTH_MAP[record["month"]]
            ).first()
            if exists:
                continue

            monthly_record = MonthlyEnergy(
                year=record["year"],
                month=MONTH_MAP[record["month"]],
                pv_production_kwh=record.get("pv_production_kwh", 0),
                pv_backfeed_kwh=record.get("pv_backfeed_kwh", 0),
                house_low_kwh=record.get("house_low_kwh", 0),
                house_high_kwh=record.get("house_high_kwh", 0),
                ev_kwh=record.get("ev_kwh", 0),
                auto_eur=Decimal(str(record.get("auto_eur", 0))),
                low_tariff_eur_per_kwh=Decimal(str(record.get("low_tariff_eur_per_kwh", 0))),
                high_tariff_eur_per_kwh=Decimal(str(record.get("high_tariff_eur_per_kwh", 0))),
                feedin_rate_eur_per_kwh=Decimal(str(record.get("feedin_rate_eur_per_kwh", 0))),
                battery_charge_kwh=record.get("battery_charge_kwh", 0),
                battery_discharge_kwh=record.get("battery_discharge_kwh", 0),
                advance_payment_eur=Decimal(str(record.get("advance_payment_eur", 0))),
                settlement_to_own_account_eur=Decimal(str(record.get("settlement_to_own_account_eur", 0))),
                billed_kwh=record.get("billed_kwh"),
                energy_unit_price_eur=Decimal(str(record.get("energy_unit_price_eur"))) if record.get("energy_unit_price_eur") else None,
            )
            db.add(monthly_record)

        print("Seeding solar investment options...")
        for option in HISTORY_DATA["solar_investment_options"]:
            exists = db.query(SolarInvestmentOption).filter_by(supplier=option["supplier"]).first()
            if exists:
                continue

            investment_option = SolarInvestmentOption(
                supplier=option["supplier"],
                panels=option["panels"],
                panel_type=option.get("panel_type"),
                total_power_wp=option.get("total_power_wp"),
                annual_production_kwh=option.get("annual_production_kwh"),
                inverter=option.get("inverter"),
                assumed_energy_price_eur_per_kwh=Decimal(str(option.get("assumed_energy_price_eur_per_kwh", 0.40))),
                total_cost_eur=Decimal(str(option.get("total_cost_eur"))),
            )
            db.add(investment_option)

        db.commit()
        print("Data seeding successful.")
    except Exception as e:
        print(f"An error occurred during data seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Running database seeder...")
    seed_data()
