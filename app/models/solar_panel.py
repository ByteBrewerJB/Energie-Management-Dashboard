from sqlalchemy import Column, Integer, String, Float, Date
from app.db.session import Base

class SolarPanel(Base):
    __tablename__ = "solar_panels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # Added a name for easier identification
    purchase_date = Column(Date, nullable=True)
    purchase_cost_eur = Column(Float, nullable=False)
    power_capacity_kwp = Column(Float, nullable=False)
    expected_yield_kwh_per_kwp = Column(Float, nullable=True)
