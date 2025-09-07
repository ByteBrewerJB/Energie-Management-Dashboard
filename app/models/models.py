from sqlalchemy import Column, Integer, String, Float, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class SolarPanel(Base):
    """
    SQLAlchemy model for a solar panel installation.
    """
    __tablename__ = "solar_panels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    purchase_date = Column(Date, nullable=False)
    purchase_cost_eur = Column(Numeric(10, 2), nullable=False)
    total_power_wp = Column(Integer, nullable=False)
    expected_annual_yield_kwh = Column(Integer)


class Battery(Base):
    """
    SQLAlchemy model for a battery installation.
    """
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    purchase_date = Column(Date, nullable=False)
    purchase_cost_eur = Column(Numeric(10, 2), nullable=False)
    capacity_kwh = Column(Float, nullable=False)


class Tariff(Base):
    """
    SQLAlchemy model for monthly energy tariffs.
    """
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    consumption_price_low_eur_kwh = Column(Numeric(10, 5), nullable=False)
    consumption_price_high_eur_kwh = Column(Numeric(10, 5), nullable=False)
    feed_in_tariff_low_eur_kwh = Column(Numeric(10, 5), nullable=False)
    feed_in_tariff_high_eur_kwh = Column(Numeric(10, 5), nullable=False)
    vat_percentage = Column(Numeric(5, 2), default=0.21)
    fixed_roi_rate_eur_kwh = Column(Numeric(10, 5), nullable=True) # This might need re-evaluation


class MonthlyMetric(Base):
    """
    SQLAlchemy model for monthly energy metrics.
    """
    __tablename__ = "monthly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(Date, nullable=False, unique=True)
    account_name = Column(String, nullable=False)
    production_total_kwh = Column(Float)
    grid_consumption_low_kwh = Column(Float)
    grid_consumption_high_kwh = Column(Float)
    grid_feed_in_low_kwh = Column(Float)
    grid_feed_in_high_kwh = Column(Float)
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)
    monthly_prepayment_eur = Column(Numeric(10, 2))


class Car(Base):
    """
    SQLAlchemy model for a car.
    """
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    usage_records = relationship("CarUsage", back_populates="car")


class CarUsage(Base):
    """
    SQLAlchemy model for monthly car usage data.
    """
    __tablename__ = "car_usage"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    total_charged_kwh = Column(Float, nullable=False)
    reimbursement_rate_eur_per_kwh = Column(Numeric(10, 5), nullable=False)

    car = relationship("Car", back_populates="usage_records")
