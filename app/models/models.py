import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Numeric,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MonthlyEnergy(Base):
    __tablename__ = 'monthly_energy'

    # --- Metadata ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # --- Invoer (BLAUW) ---
    # Tarieven
    low_tariff_eur_per_kwh = Column(Numeric(10, 5))
    high_tariff_eur_per_kwh = Column(Numeric(10, 5))
    feedin_rate_eur_per_kwh = Column(Numeric(10, 5))
    vat_rate = Column(Numeric(4, 3), default=0.21)

    # Auto
    ev_kwh = Column(Float, default=0.0)
    auto_eur = Column(Numeric(10, 2), default=0.0)

    # Zonnepanelen
    pv_backfeed_kwh = Column(Float, default=0.0)
    pv_production_kwh = Column(Float, default=0.0) # Kan handmatig of uit SolarMonthlyReference komen

    # Huisverbruik
    house_low_kwh = Column(Float, default=0.0)
    house_high_kwh = Column(Float, default=0.0)

    # Batterij
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)

    # Net zonder batterij (optioneel)
    grid_import_without_battery_kwh = Column(Float, nullable=True)
    grid_export_without_battery_kwh = Column(Float, nullable=True)

    # Financieel
    advance_payment_eur = Column(Numeric(10, 2), default=0.0)
    settlement_to_own_account_eur = Column(Numeric(10, 2), default=0.0)

    # Overig
    provider_name = Column(String, default="Awesems")
    note = Column(String, nullable=True)

    # --- (Optioneel) Factuurvelden ---
    billed_kwh = Column(Float, nullable=True)
    energy_unit_price_eur = Column(Numeric(10, 5), nullable=True)

    __table_args__ = (UniqueConstraint('year', 'month', name='_year_month_uc'),)


class SolarInvestmentOption(Base):
    __tablename__ = 'solar_investment_option'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier = Column(String, nullable=False)
    panels = Column(Integer, nullable=False)
    panel_type = Column(String)
    total_power_wp = Column(Integer)
    annual_production_kwh = Column(Float)
    inverter = Column(String)
    assumed_energy_price_eur_per_kwh = Column(Numeric(10, 5), default=0.40)
    total_cost_eur = Column(Numeric(10, 2))


class SolarMonthlyReference(Base):
    __tablename__ = 'solar_monthly_reference'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    pv_production_kwh = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('year', 'month', name='_solar_ref_year_month_uc'),)
