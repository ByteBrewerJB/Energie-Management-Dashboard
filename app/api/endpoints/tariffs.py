from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.tariff import Tariff, TariffCreate, TariffUpdate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Tariff, status_code=status.HTTP_201_CREATED)
def create_tariff(
    tariff_in: TariffCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new tariff.
    """
    return crud.tariff.create_tariff(db=db, tariff=tariff_in)


@router.get("/", response_model=List[Tariff])
def read_tariffs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve tariffs.
    """
    return crud.tariff.get_tariffs(db, skip=skip, limit=limit)


@router.get("/{tariff_id}", response_model=Tariff)
def read_tariff(
    tariff_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific tariff by ID.
    """
    db_tariff = crud.tariff.get_tariff(db, tariff_id=tariff_id)
    if db_tariff is None:
        raise HTTPException(status_code=404, detail="Tariff not found")
    return db_tariff


@router.put("/{tariff_id}", response_model=Tariff)
def update_tariff(
    tariff_id: int,
    tariff_in: TariffUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a tariff.
    """
    db_tariff = crud.tariff.get_tariff(db, tariff_id=tariff_id)
    if not db_tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    return crud.tariff.update_tariff(db=db, tariff_id=tariff_id, tariff_in=tariff_in)


@router.delete("/{tariff_id}", response_model=Tariff)
def delete_tariff(
    tariff_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a tariff.
    """
    db_tariff = crud.tariff.get_tariff(db, tariff_id=tariff_id)
    if not db_tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    return crud.tariff.delete_tariff(db=db, tariff_id=tariff_id)
