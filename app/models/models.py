from sqlalchemy import Column, Integer, String, Float, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

# --- One-time Installation Models ---

class SolarPanel(Base):
    """
    SQLAlchemy model for a solar panel installation.
    Represents a one-time setup.
    """
    __tablename__ = "solar_panels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Zonnepanelen")
    purchase_date = Column(Date, nullable=False)
    purchase_cost_eur = Column(Numeric(10, 2), nullable=False)
    total_power_wp = Column(Integer, nullable=False)
    expected_annual_yield_kwh = Column(Integer)


class Battery(Base):
    """
    SQLAlchemy model for a battery installation.
    Represents a one-time setup.
    """
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Batterij")
    brand = Column(String)
    purchase_date = Column(Date, nullable=False)
    purchase_cost_eur = Column(Numeric(10, 2), nullable=False)
    capacity_kwh = Column(Float, nullable=False)


class Car(Base):
    """
    SQLAlchemy model for an electric car.
    Represents a vehicle whose charging can be reimbursed.
    """
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    reimbursement_rate_eur_per_kwh = Column(Numeric(10, 5), nullable=False)

    journal_entries = relationship("CarJournalEntry", back_populates="car")


# --- Monthly Journaling Models ---

class MonthlyJournal(Base):
    """
    Central SQLAlchemy model for all monthly data.
    This model consolidates metrics, tariffs, and links to car usage.
    """
    __tablename__ = "monthly_journal"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # --- Metrics from the energy provider ---
    grid_consumption_low_kwh = Column(Float, nullable=False)
    grid_consumption_high_kwh = Column(Float, nullable=False)
    grid_feed_in_low_kwh = Column(Float, nullable=False)
    grid_feed_in_high_kwh = Column(Float, nullable=False)

    # --- Tariffs for this month ---
    consumption_price_low_eur_kwh = Column(Numeric(10, 5), nullable=False)
    consumption_price_high_eur_kwh = Column(Numeric(10, 5), nullable=False)
    feed_in_tariff_low_eur_kwh = Column(Numeric(10, 5), nullable=False)
    feed_in_tariff_high_eur_kwh = Column(Numeric(10, 5), nullable=False)

    # --- Internal metrics & settings ---
    solar_production_kwh = Column(Float, nullable=False)
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)
    monthly_prepayment_eur = Column(Numeric(10, 2), nullable=False)

    # --- Relationships ---
    car_entries = relationship("CarJournalEntry", back_populates="journal", cascade="all, delete-orphan")


class CarJournalEntry(Base):
    """
    SQLAlchemy model for monthly car charging data, linked to a MonthlyJournal.
    """
    __tablename__ = "car_journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("monthly_journal.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    total_charged_kwh = Column(Float, nullable=False)

    journal = relationship("MonthlyJournal", back_populates="car_entries")
    car = relationship("Car", back_populates="journal_entries")
