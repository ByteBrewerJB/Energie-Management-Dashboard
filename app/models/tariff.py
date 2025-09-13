from sqlalchemy import Column, Integer, Float, Date
from app.db.session import Base

class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    purchase_low_eur_kwh = Column(Float, nullable=False)
    purchase_high_eur_kwh = Column(Float, nullable=False)
    sale_eur_kwh = Column(Float, nullable=False)
    vat = Column(Float, nullable=False)
    fixed_roi_rate = Column(Float, nullable=True)
