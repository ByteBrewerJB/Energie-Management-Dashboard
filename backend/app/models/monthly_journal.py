from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from ..db.base import Base


class MonthlyJournal(Base):
    __tablename__ = "monthly_journals"
    __table_args__ = (
        UniqueConstraint("owner_id", "year", "month", name="uq_journal_owner_year_month"),
    )

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    consumption_tariff_1_kwh = Column(Float, nullable=True)
    consumption_tariff_2_kwh = Column(Float, nullable=True)
    feed_in_without_battery_kwh = Column(Float, nullable=True)
    total_house_consumption_kwh = Column(Float, nullable=True)
    avg_consumption_tariff_low_eur_kwh = Column(Float, nullable=True)
    avg_consumption_tariff_high_eur_kwh = Column(Float, nullable=True)
    supplier_costs_eur = Column(Float, nullable=True)
    avg_feed_in_tariff_eur_kwh = Column(Float, nullable=True)
    solar_production_kwh = Column(Float, nullable=True)
    battery_charge_kwh = Column(Float, nullable=True)
    battery_discharge_kwh = Column(Float, nullable=True)
    advance_payment_eur = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="journal_entries")
    car_charges = relationship("CarChargeJournal", back_populates="journal", cascade="all, delete-orphan")
