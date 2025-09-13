from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.battery import Battery, BatteryCreate, BatteryUpdate
from app.crud import crud_battery

router = APIRouter()

@router.get("/batteries", response_model=List[Battery])
def read_batteries(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all battery installations.
    """
    batteries = crud_battery.get_multi(db, skip=skip, limit=limit)
    return batteries


@router.post("/batteries", response_model=Battery, status_code=status.HTTP_201_CREATED)
def create_battery(
    *,
    db: Session = Depends(get_db),
    battery_in: BatteryCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new battery installation.
    """
    battery = crud_battery.create(db=db, obj_in=battery_in)
    return battery


@router.get("/batteries/{battery_id}", response_model=Battery)
def read_battery(
    *,
    db: Session = Depends(get_db),
    battery_id: int,
) -> Any:
    """
    Get a specific battery installation by its ID.
    """
    battery = crud_battery.get(db, battery_id=battery_id)
    if not battery:
        raise HTTPException(status_code=404, detail="Battery installation not found")
    return battery


@router.put("/batteries/{battery_id}", response_model=Battery)
def update_battery(
    *,
    db: Session = Depends(get_db),
    battery_id: int,
    battery_in: BatteryUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing battery installation.
    """
    battery = crud_battery.get(db, battery_id=battery_id)
    if not battery:
        raise HTTPException(status_code=404, detail="Battery installation not found")

    battery = crud_battery.update(db=db, db_obj=battery, obj_in=battery_in)
    return battery


@router.delete("/batteries/{battery_id}", response_model=Battery)
def delete_battery(
    *,
    db: Session = Depends(get_db),
    battery_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a battery installation.
    """
    battery = crud_battery.get(db, battery_id=battery_id)
    if not battery:
        raise HTTPException(status_code=404, detail="Battery installation not found")

    battery = crud_battery.remove(db=db, battery_id=battery_id)
    return battery
