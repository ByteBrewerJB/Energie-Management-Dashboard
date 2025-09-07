from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.solar_panel import SolarPanel, SolarPanelCreate, SolarPanelUpdate
from app.crud import crud_solar_panel

router = APIRouter()

@router.get("/investments", response_model=List[SolarPanel])
def read_investments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all solar panel installations (investments).
    """
    investments = crud_solar_panel.get_multi(db, skip=skip, limit=limit)
    return investments


@router.post("/investments", response_model=SolarPanel, status_code=status.HTTP_201_CREATED)
def create_investment(
    *,
    db: Session = Depends(get_db),
    solar_panel_in: SolarPanelCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new solar panel installation (investment).
    """
    investment = crud_solar_panel.create(db=db, obj_in=solar_panel_in)
    return investment


@router.get("/investments/{investment_id}", response_model=SolarPanel)
def read_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
) -> Any:
    """
    Get a specific solar panel installation by its ID.
    """
    investment = crud_solar_panel.get(db, solar_panel_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment


@router.put("/investments/{investment_id}", response_model=SolarPanel)
def update_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
    solar_panel_in: SolarPanelUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing solar panel installation.
    """
    investment = crud_solar_panel.get(db, solar_panel_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    investment = crud_solar_panel.update(db=db, db_obj=investment, obj_in=solar_panel_in)
    return investment


@router.delete("/investments/{investment_id}", response_model=SolarPanel)
def delete_investment(
    *,
    db: Session = Depends(get_db),
    investment_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a solar panel installation.
    """
    investment = crud_solar_panel.get(db, solar_panel_id=investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    investment = crud_solar_panel.remove(db=db, solar_panel_id=investment_id)
    return investment
