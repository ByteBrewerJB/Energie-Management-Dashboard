from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.models import MonthlyEnergy
from app.schemas import monthly_energy as monthly_energy_schema
from app.crud import crud_monthly_energy
from app.api import deps
from app.services.calculations import calculate_monthly_metrics

# Helper to add month names
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

router = APIRouter()

def enrich_record(db_obj: MonthlyEnergy) -> monthly_energy_schema.MonthlyEnergyRead:
    """
    Enriches a database record with calculated metrics.
    """
    calculated_data = calculate_monthly_metrics(db_obj)
    response_data = monthly_energy_schema.MonthlyEnergyRead.from_orm(db_obj)
    response_data.month_name = MONTH_NAMES.get(db_obj.month)
    for key, value in calculated_data.items():
        setattr(response_data, key, value)
    return response_data

@router.get("/", response_model=List[monthly_energy_schema.MonthlyEnergyRead])
def read_monthly_energies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all monthly energy records.
    """
    records = crud_monthly_energy.get_multi(db, skip=skip, limit=limit)
    return [enrich_record(record) for record in records]

@router.post("/", response_model=monthly_energy_schema.MonthlyEnergyRead)
def create_monthly_energy(
    *,
    db: Session = Depends(deps.get_db),
    monthly_energy_in: monthly_energy_schema.MonthlyEnergyCreate,
) -> Any:
    """
    Create new monthly energy record.
    """
    record = crud_monthly_energy.create(db, obj_in=monthly_energy_in)
    return enrich_record(record)

@router.get("/{id}", response_model=monthly_energy_schema.MonthlyEnergyRead)
def read_monthly_energy(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Get monthly energy record by ID.
    """
    record = crud_monthly_energy.get(db, id=id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return enrich_record(record)

@router.put("/{id}", response_model=monthly_energy_schema.MonthlyEnergyRead)
def update_monthly_energy(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    monthly_energy_in: monthly_energy_schema.MonthlyEnergyUpdate,
) -> Any:
    """
    Update a monthly energy record.
    """
    record = crud_monthly_energy.get(db, id=id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    updated_record = crud_monthly_energy.update(db, db_obj=record, obj_in=monthly_energy_in)
    return enrich_record(updated_record)

@router.delete("/{id}", response_model=monthly_energy_schema.MonthlyEnergyRead)
def delete_monthly_energy(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Delete a monthly energy record.
    """
    record = crud_monthly_energy.get(db, id=id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    deleted_record = crud_monthly_energy.remove(db, id=id)
    return enrich_record(deleted_record) # enrich for response consistency
