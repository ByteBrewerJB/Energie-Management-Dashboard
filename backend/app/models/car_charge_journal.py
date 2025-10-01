from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from ..db.base import Base


class CarChargeJournal(Base):
    __tablename__ = "car_charge_journals"
    __table_args__ = (
        UniqueConstraint("journal_id", "car_id", name="uq_journal_car"),
    )

    id = Column(Integer, primary_key=True, index=True)
    charged_kwh = Column(Float, nullable=False, default=0.0)
    journal_id = Column(Integer, ForeignKey("monthly_journals.id", ondelete="CASCADE"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)

    journal = relationship("MonthlyJournal", back_populates="car_charges")
    car = relationship("Car", back_populates="charges")
