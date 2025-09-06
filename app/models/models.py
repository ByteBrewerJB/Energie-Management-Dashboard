from sqlalchemy import Column, Integer, String, Float, Date, Numeric
from app.db.session import Base

# 1. Installatie en Investering (System Setup & Investment)
class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, default="Zonnepaneelinstallatie")
    install_date = Column(Date, nullable=False)
    total_investment_cost = Column(Numeric(10, 2), nullable=False)
    total_wp = Column(Integer, nullable=False)
    estimated_annual_production_kwh = Column(Integer)
    inverter_type = Column(String)

# 2. Energie Tarieven (Tariffs)
class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True) # Nullable for the currently active tariff
    purchase_rate_low = Column(Numeric(10, 5), nullable=False)
    purchase_rate_high = Column(Numeric(10, 5), nullable=False)
    feed_in_rate = Column(Numeric(10, 5), nullable=False)
    vat_percentage = Column(Numeric(5, 2), default=21.00)
    fixed_roi_rate = Column(Numeric(10, 5), nullable=True) # For the "Excel method"

# 3. Maandelijkse Metingen (Monthly Metrics)
class MonthlyMetric(Base):
    __tablename__ = "monthly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(Date, nullable=False, unique=True) # Store as the first day of the month
    account = Column(String, default="household") # To support multi-account in the future

    # Production
    total_generated_kwh = Column(Float)

    # Import from grid
    import_low_rate_kwh = Column(Float)
    import_high_rate_kwh = Column(Float)

    # Export to grid
    total_feed_in_kwh = Column(Float)

    # Consumption breakdown
    ev_consumption_kwh = Column(Float)

    # Battery activity
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)

    # Financial
    prepayment_amount = Column(Numeric(10, 2))
