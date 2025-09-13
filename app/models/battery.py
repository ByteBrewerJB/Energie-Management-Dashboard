from sqlalchemy import Column, Integer, String, Float, Date
from app.db.session import Base

class Battery(Base):
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_cost_eur = Column(Float, nullable=False)
    capacity_kwh = Column(Float, nullable=False)
