from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, get_db_session
from ..models.car import Car
from ..models.user import User
from ..schemas.car import CarCreate, CarRead, CarUpdate

router = APIRouter()


@router.get("/", response_model=List[CarRead])
def list_cars(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[Car]:
    return (
        db.query(Car)
        .filter(Car.owner_id == current_user.id)
        .order_by(Car.is_active.desc(), Car.name.asc())
        .all()
    )


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
def create_car(
    car_in: CarCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Car:
    car = Car(owner_id=current_user.id, **car_in.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


@router.put("/{car_id}", response_model=CarRead)
def update_car(
    car_id: int,
    car_in: CarUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Car:
    car = db.query(Car).filter(Car.id == car_id, Car.owner_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto niet gevonden")

    for field, value in car_in.model_dump(exclude_unset=True).items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    car = db.query(Car).filter(Car.id == car_id, Car.owner_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto niet gevonden")
    db.delete(car)
    db.commit()
