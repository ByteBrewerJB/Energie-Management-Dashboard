from sqlalchemy.orm import Session
from app.models import models
from app.schemas import investment as investment_schema

def get_investment(db: Session, investment_id: int):
    return db.query(models.Investment).filter(models.Investment.id == investment_id).first()

def get_investments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Investment).offset(skip).limit(limit).all()

def create_investment(db: Session, investment: investment_schema.InvestmentCreate):
    db_investment = models.Investment(**investment.dict())
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment

def update_investment(db: Session, investment_id: int, investment: investment_schema.InvestmentCreate):
    db_investment = db.query(models.Investment).filter(models.Investment.id == investment_id).first()
    if db_investment:
        for key, value in investment.dict().items():
            setattr(db_investment, key, value)
        db.commit()
        db.refresh(db_investment)
    return db_investment

def delete_investment(db: Session, investment_id: int):
    db_investment = db.query(models.Investment).filter(models.Investment.id == investment_id).first()
    if db_investment:
        db.delete(db_investment)
        db.commit()
    return db_investment
