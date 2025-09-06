from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.tariff import Tariff, TariffCreate, TariffUpdate
from app.crud import crud_tariffs
from app.models import models

router = APIRouter()

@router.get("/tariffs", response_model=List[Tariff])
def read_tariffs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all tariffs.

    Args:
        db: The database session dependency.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.
        current_user: The authenticated user dependency.

    Returns:
        A list of Tariff objects.
    """
    tariffs = crud_tariffs.get_multi(db, skip=skip, limit=limit)
    return tariffs


@router.post("/tariffs", response_model=Tariff, status_code=status.HTTP_201_CREATED)
def create_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_in: TariffCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new tariff.

    Args:
        db: The database session dependency.
        tariff_in: The tariff data from the request body.
        current_user: The authenticated user dependency.

    Returns:
        The newly created Tariff object.
    """
    tariff = crud_tariffs.create(db=db, obj_in=tariff_in)
    return tariff


@router.get("/tariffs/{tariff_id}", response_model=Tariff)
def read_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific tariff by its ID.

    Args:
        db: The database session dependency.
        tariff_id: The ID of the tariff to retrieve.
        current_user: The authenticated user dependency.

    Returns:
        The requested Tariff object.

    Raises:
        HTTPException: 404 Not Found if the tariff does not exist.
    """
    tariff = crud_tariffs.get(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    return tariff


@router.put("/tariffs/{tariff_id}", response_model=Tariff)
def update_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    tariff_in: TariffUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing tariff.

    Args:
        db: The database session dependency.
        tariff_id: The ID of the tariff to update.
        tariff_in: The new tariff data from the request body.
        current_user: The authenticated user dependency.

    Returns:
        The updated Tariff object.

    Raises:
        HTTPException: 404 Not Found if the tariff does not exist.
    """
    tariff = crud_tariffs.get(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")

    tariff = crud_tariffs.update(db=db, db_obj=tariff, obj_in=tariff_in)
    return tariff


@router.delete("/tariffs/{tariff_id}", response_model=Tariff)
def delete_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a tariff.

    Args:
        db: The database session dependency.
        tariff_id: The ID of the tariff to delete.
        current_user: The authenticated user dependency.

    Returns:
        The deleted Tariff object.

    Raises:
        HTTPException: 404 Not Found if the tariff does not exist.
    """
    tariff = crud_tariffs.get(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")

    tariff = crud_tariffs.remove(db=db, tariff_id=tariff_id)
    return tariff
