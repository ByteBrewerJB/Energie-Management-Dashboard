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
    Retrieve all investments.

    This is a protected endpoint intended for the admin panel.

    Args:
        db: The database session dependency.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.
        current_user: The authenticated user dependency.

    Returns:
        A list of Investment objects.
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

    Args:
        db: The database session dependency.
        investment_in: The investment data from the request body.
        current_user: The authenticated user dependency.

    Returns:
        The newly created Investment object.
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
    Get a specific investment by its ID.

    This is a public endpoint.

    Args:
        db: The database session dependency.
        investment_id: The ID of the investment to retrieve.

    Returns:
        The requested Investment object.

    Raises:
        HTTPException: 404 Not Found if the investment does not exist.
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
    Update an existing investment.

    Args:
        db: The database session dependency.
        investment_id: The ID of the investment to update.
        investment_in: The new investment data from the request body.
        current_user: The authenticated user dependency.

    Returns:
        The updated Investment object.

    Raises:
        HTTPException: 404 Not Found if the investment does not exist.
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

    Args:
        db: The database session dependency.
        investment_id: The ID of the investment to delete.
        current_user: The authenticated user dependency.

    Returns:
        The deleted Investment object.

    Raises:
        HTTPException: 404 Not Found if the investment does not exist.
    """
    investment = crud_investments.get(db, investment_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    investment = crud_investments.remove(db=db, investment_id=investment_id)
    return investment
