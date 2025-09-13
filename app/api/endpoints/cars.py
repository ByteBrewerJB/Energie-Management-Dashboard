from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.car import Car, CarCreate, CarUpdate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(
    car_in: CarCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new car.
    """
    return crud.car.create_car(db=db, car=car_in)


@router.get("/", response_model=List[Car])
def read_cars(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve cars.
    """
    return crud.car.get_cars(db, skip=skip, limit=limit)


@router.get("/{car_id}", response_model=Car)
def read_car(
    car_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific car by ID.
    """
    db_car = crud.car.get_car(db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


@router.put("/{car_id}", response_model=Car)
def update_car(
    car_id: int,
    car_in: CarUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a car.
    """
    db_car = crud.car.get_car(db, car_id=car_id)
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return crud.car.update_car(db=db, car_id=car_id, car_in=car_in)


@router.delete("/{car_id}", response_model=Car)
def delete_car(
    car_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a car.
    """
    db_car = crud.car.get_car(db, car_id=car_id)
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return crud.car.delete_car(db=db, car_id=car_id)
