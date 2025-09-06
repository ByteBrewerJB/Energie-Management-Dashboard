from sqlalchemy import Column, Integer, String, Float, Date, Numeric
from app.db.session import Base

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    installation_date = Column(Date, nullable=False)
    total_cost_eur = Column(Numeric(10, 2), nullable=False)
    total_power_wp = Column(Integer, nullable=False)
    estimated_annual_production_kwh = Column(Integer)

class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    purchase_low_eur_kwh = Column(Numeric(10, 5), nullable=False)
    purchase_high_eur_kwh = Column(Numeric(10, 5), nullable=False)
    sale_eur_kwh = Column(Numeric(10, 5), nullable=False)
    vat_percentage = Column(Numeric(5, 2), default=0.21)
    fixed_roi_rate_eur_kwh = Column(Numeric(10, 5), nullable=True)

class MonthlyMetric(Base):
    __tablename__ = "monthly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(Date, nullable=False, unique=True)
    account_name = Column(String, nullable=False)
    production_total_kwh = Column(Float)
    import_low_kwh = Column(Float)
    import_high_kwh = Column(Float)
    export_total_kwh = Column(Float)
    consumption_ev_kwh = Column(Float)
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)
    monthly_prepayment_eur = Column(Numeric(10, 2))
