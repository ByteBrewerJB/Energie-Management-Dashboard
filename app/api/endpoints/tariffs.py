from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas import tariff as tariff_schema
from app.crud import crud_tariffs

router = APIRouter()

@router.post("/tariffs", response_model=tariff_schema.TariffInDB)
def create_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_in: tariff_schema.TariffCreate
):
    tariff = crud_tariffs.create_tariff(db=db, tariff=tariff_in)
    return tariff

@router.get("/tariffs", response_model=List[tariff_schema.TariffInDB])
def read_tariffs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    tariffs = crud_tariffs.get_tariffs(db, skip=skip, limit=limit)
    return tariffs

@router.get("/tariffs/{tariff_id}", response_model=tariff_schema.TariffInDB)
def read_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
):
    tariff = crud_tariffs.get_tariff(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    return tariff

@router.put("/tariffs/{tariff_id}", response_model=tariff_schema.TariffInDB)
def update_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
    tariff_in: tariff_schema.TariffCreate,
):
    tariff = crud_tariffs.get_tariff(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    tariff = crud_tariffs.update_tariff(db=db, tariff_id=tariff_id, tariff=tariff_in)
    return tariff

@router.delete("/tariffs/{tariff_id}", response_model=tariff_schema.TariffInDB)
def delete_tariff(
    *,
    db: Session = Depends(get_db),
    tariff_id: int,
):
    tariff = crud_tariffs.get_tariff(db, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    tariff = crud_tariffs.delete_tariff(db=db, tariff_id=tariff_id)
    return tariff
