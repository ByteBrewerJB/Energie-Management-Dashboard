from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    reimbursement_rate_eur_per_kwh = Column(Float, nullable=False)
