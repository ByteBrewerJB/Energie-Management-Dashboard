from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.tariff import Tariff, TariffCreate, TariffUpdate
from app.crud import crud_tariff

router = APIRouter()

@router.get("/", response_model=List[Tariff])
def read_tariffs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all tariffs.
    """
    tariffs = crud_tariff.get_multi(db, skip=skip, limit=limit)
    return tariffs


@router.post("/", response_model=Tariff, status_code=status.HTTP_201_CREATED)
def create_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_in: TariffCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new tariff.
    """
    tariff = crud_tariff.create(db=db, obj_in=tariff_in)
    return tariff


@router.get("/{tariff_id}", response_model=Tariff)
def read_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific tariff by its ID.
    """
    tariff = crud_tariff.get(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    return tariff


@router.put("/{tariff_id}", response_model=Tariff)
def update_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    tariff_in: TariffUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing tariff.
    """
    tariff = crud_tariff.get(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")

    tariff = crud_tariff.update(db=db, db_obj=tariff, obj_in=tariff_in)
    return tariff


@router.delete("/{tariff_id}", response_model=Tariff)
def delete_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a tariff.
    """
    tariff = crud_tariff.get(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")

    tariff = crud_tariff.remove(db=db, tariff_id=tariff_id)
    return tariff
