from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base import Base


class SolarPanelInstallation(Base):
    __tablename__ = "solar_panel_installations"

    id = Column(Integer, primary_key=True, index=True)
    purchase_date = Column(Date, nullable=True)
    purchase_cost_eur = Column(Float, nullable=True)
    total_power_wp = Column(Integer, nullable=True)
    expected_annual_yield_kwh = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="solar_installation", uselist=False)


class Battery(Base):
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)
    purchase_date = Column(Date, nullable=True)
    purchase_cost_eur = Column(Float, nullable=True)
    capacity_kwh = Column(Float, nullable=True)
    brand_model = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="battery", uselist=False)
