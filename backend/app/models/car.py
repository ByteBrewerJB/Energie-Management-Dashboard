from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    reimbursement_rate_ex_vat_eur_kwh = Column(Float, nullable=True)
    reimbursement_rate_inc_vat_eur_kwh = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="cars")
    charges = relationship("CarChargeJournal", back_populates="car", cascade="all, delete-orphan")
