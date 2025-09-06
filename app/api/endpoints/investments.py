from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.investment import Investment, InvestmentCreate, InvestmentUpdate
from app.crud import crud_investments
from app.models import models

router = APIRouter()

@router.get("/investments", response_model=List[Investment])
def read_investments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all investments. Protected route for admin panel.
    """
    investments = crud_investments.get_multi(db, skip=skip, limit=limit)
    return investments


@router.post("/investments", response_model=Investment, status_code=status.HTTP_201_CREATED)
def create_investment(
    *,
    db: Session = Depends(get_db),
    investment_in: InvestmentCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new investment.
    """
    investment = crud_investments.create(db=db, obj_in=investment_in)
    return investment


@router.get("/investments/{investment_id}", response_model=Investment)
def read_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
) -> Any:
    """
    Get a specific investment by ID. This is a public endpoint.
    """
    investment = crud_investments.get(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment


@router.put("/investments/{investment_id}", response_model=Investment)
def update_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
    investment_in: InvestmentUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an investment.
    """
    investment = crud_investments.get(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    investment = crud_investments.update(db=db, db_obj=investment, obj_in=investment_in)
    return investment


@router.delete("/investments/{investment_id}", response_model=Investment)
def delete_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an investment.
    """
    investment = crud_investments.get(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    investment = crud_investments.remove(db=db, investment_id=investment_id)
    return investment
