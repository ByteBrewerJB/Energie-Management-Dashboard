from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class MonthlyJournal(Base):
    __tablename__ = "monthly_journal"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # Grid Interaction
    grid_consumption_low_kwh = Column(Float, default=0.0)
    grid_consumption_high_kwh = Column(Float, default=0.0)
    grid_feed_in_low_kwh = Column(Float, default=0.0)
    grid_feed_in_high_kwh = Column(Float, default=0.0)

    # Pricing and Tariffs
    consumption_price_low_eur_kwh = Column(Float, default=0.0)
    consumption_price_high_eur_kwh = Column(Float, default=0.0)
    feed_in_tariff_low_eur_kwh = Column(Float, default=0.0)
    feed_in_tariff_high_eur_kwh = Column(Float, default=0.0)

    # Local Generation and Storage
    solar_production_kwh = Column(Float, default=0.0)
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)

    # Financials
    monthly_prepayment_eur = Column(Float, default=0.0)

    # Car Charging
    car_journal_entries = relationship("CarJournalEntry", back_populates="monthly_journal")


class CarJournalEntry(Base):
    __tablename__ = "car_journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    total_charged_kwh = Column(Float, nullable=False)

    monthly_journal_id = Column(Integer, ForeignKey("monthly_journal.id"))
    monthly_journal = relationship("MonthlyJournal", back_populates="car_journal_entries")

    car_id = Column(Integer, ForeignKey("cars.id"))
    car = relationship("Car")

    entity_id = Column(Integer, ForeignKey("entities.id"))
    entity = relationship("Entity")
