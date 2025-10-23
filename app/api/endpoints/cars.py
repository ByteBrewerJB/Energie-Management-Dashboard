from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.car import Car, CarCreate, CarUpdate
from app.crud import crud_car

router = APIRouter()

@router.get("/", response_model=List[Car])
def read_cars(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all cars.
    """
    cars = crud_car.get_multi(db, skip=skip, limit=limit)
    return cars


@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(
    *,
    db: Session = Depends(get_db),
    car_in: CarCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new car.
    """
    car = crud_car.get_by_name(db, name=car_in.name)
    if car:
        raise HTTPException(
            status_code=400,
            detail="A car with this name already exists.",
        )
    car = crud_car.create(db=db, obj_in=car_in)
    return car


@router.get("/{car_id}", response_model=Car)
def read_car(
    *,
    db: Session = Depends(get_db),
    car_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific car by its ID.
    """
    car = crud_car.get(db, car_id=car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.put("/{car_id}", response_model=Car)
def update_car(
    *,
    db: Session = Depends(get_db),
    car_id: int,
    car_in: CarUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing car.
    """
    car = crud_car.get(db, car_id=car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car = crud_car.update(db=db, db_obj=car, obj_in=car_in)
    return car


@router.delete("/{car_id}", response_model=Car)
def delete_car(
    *,
    db: Session = Depends(get_db),
    car_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a car.
    """
    car = crud_car.get(db, car_id=car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car = crud_car.remove(db=db, car_id=car_id)
    return car
