from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.battery import Battery, BatteryCreate, BatteryUpdate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Battery, status_code=status.HTTP_201_CREATED)
def create_battery(
    battery_in: BatteryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new battery.
    """
    return crud.battery.create_battery(db=db, battery=battery_in)


@router.get("/", response_model=List[Battery])
def read_batteries(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve batteries.
    """
    return crud.battery.get_batteries(db, skip=skip, limit=limit)


@router.get("/{battery_id}", response_model=Battery)
def read_battery(
    battery_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific battery by ID.
    """
    db_battery = crud.battery.get_battery(db, battery_id=battery_id)
    if db_battery is None:
        raise HTTPException(status_code=404, detail="Battery not found")
    return db_battery


@router.put("/{battery_id}", response_model=Battery)
def update_battery(
    battery_id: int,
    battery_in: BatteryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a battery.
    """
    db_battery = crud.battery.get_battery(db, battery_id=battery_id)
    if not db_battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    return crud.battery.update_battery(db=db, battery_id=battery_id, battery_in=battery_in)


@router.delete("/{battery_id}", response_model=Battery)
def delete_battery(
    battery_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a battery.
    """
    db_battery = crud.battery.get_battery(db, battery_id=battery_id)
    if not db_battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    return crud.battery.delete_battery(db=db, battery_id=battery_id)
