from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.models import SolarInvestmentOption
from app.schemas import solar_investment as solar_investment_schema
from app.crud import crud_solar_investment
from app.api import deps
from app.services.calculations import calculate_investment_metrics

router = APIRouter()

def enrich_record(db_obj: SolarInvestmentOption) -> solar_investment_schema.SolarInvestmentRead:
    """
    Enriches a database record with calculated metrics.
    """
    calculated_data = calculate_investment_metrics(db_obj)
    response_data = solar_investment_schema.SolarInvestmentRead.from_orm(db_obj)
    for key, value in calculated_data.items():
        setattr(response_data, key, value)
    return response_data

@router.get("/", response_model=List[solar_investment_schema.SolarInvestmentRead])
def read_solar_investments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all solar investment options.
    """
    records = crud_solar_investment.get_multi(db, skip=skip, limit=limit)
    return [enrich_record(record) for record in records]

@router.post("/", response_model=solar_investment_schema.SolarInvestmentRead)
def create_solar_investment(
    *,
    db: Session = Depends(deps.get_db),
    solar_investment_in: solar_investment_schema.SolarInvestmentCreate,
) -> Any:
    """
    Create new solar investment option.
    """
    record = crud_solar_investment.create(db, obj_in=solar_investment_in)
    return enrich_record(record)

@router.get("/{id}", response_model=solar_investment_schema.SolarInvestmentRead)
def read_solar_investment(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Get solar investment option by ID.
    """
    record = crud_solar_investment.get(db, id=id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return enrich_record(record)

@router.put("/{id}", response_model=solar_investment_schema.SolarInvestmentRead)
def update_solar_investment(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    solar_investment_in: solar_investment_schema.SolarInvestmentUpdate,
) -> Any:
    """
    Update a solar investment option.
    """
    record = crud_solar_investment.get(db, id=id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    updated_record = crud_solar_investment.update(db, db_obj=record, obj_in=solar_investment_in)
    return enrich_record(updated_record)

@router.delete("/{id}", response_model=solar_investment_schema.SolarInvestmentRead)
def delete_solar_investment(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Delete a solar investment option.
    """
    record = crud_solar_investment.get(db, id=id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    deleted_record = crud_solar_investment.remove(db, id=id)
    return enrich_record(deleted_record)
