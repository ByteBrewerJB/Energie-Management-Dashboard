from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas import investment as investment_schema
from app.crud import crud_investments

router = APIRouter()

@router.post("/investments", response_model=investment_schema.InvestmentInDB)
def create_investment(
    *,
    db: Session = Depends(get_db),
    investment_in: investment_schema.InvestmentCreate
):
    investment = crud_investments.create_investment(db=db, investment=investment_in)
    return investment

@router.get("/investments", response_model=List[investment_schema.InvestmentInDB])
def read_investments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    investments = crud_investments.get_investments(db, skip=skip, limit=limit)
    return investments

@router.get("/investments/{investment_id}", response_model=investment_schema.InvestmentInDB)
def read_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
):
    investment = crud_investments.get_investment(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment

@router.put("/investments/{investment_id}", response_model=investment_schema.InvestmentInDB)
def update_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
    investment_in: investment_schema.InvestmentCreate,
):
    investment = crud_investments.get_investment(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    investment = crud_investments.update_investment(db=db, investment_id=investment_id, investment=investment_in)
    return investment

@router.delete("/investments/{investment_id}", response_model=investment_schema.InvestmentInDB)
def delete_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
):
    investment = crud_investments.get_investment(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    investment = crud_investments.delete_investment(db=db, investment_id=investment_id)
    return investment
