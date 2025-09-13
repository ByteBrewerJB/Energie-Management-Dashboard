from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.solar_panel import SolarPanel, SolarPanelCreate, SolarPanelUpdate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=SolarPanel, status_code=status.HTTP_201_CREATED)
def create_solar_panel(
    solar_panel_in: SolarPanelCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new solar panel installation.
    """
    return crud.solar_panel.create_solar_panel(db=db, solar_panel=solar_panel_in)


@router.get("/", response_model=List[SolarPanel])
def read_solar_panels(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve solar panel installations.
    """
    return crud.solar_panel.get_solar_panels(db, skip=skip, limit=limit)


@router.get("/{solar_panel_id}", response_model=SolarPanel)
def read_solar_panel(
    solar_panel_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific solar panel installation by ID.
    """
    db_solar_panel = crud.solar_panel.get_solar_panel(db, solar_panel_id=solar_panel_id)
    if db_solar_panel is None:
        raise HTTPException(status_code=404, detail="SolarPanel not found")
    return db_solar_panel


@router.put("/{solar_panel_id}", response_model=SolarPanel)
def update_solar_panel(
    solar_panel_id: int,
    solar_panel_in: SolarPanelUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a solar panel installation.
    """
    db_solar_panel = crud.solar_panel.get_solar_panel(db, solar_panel_id=solar_panel_id)
    if not db_solar_panel:
        raise HTTPException(status_code=404, detail="SolarPanel not found")
    return crud.solar_panel.update_solar_panel(db=db, solar_panel_id=solar_panel_id, solar_panel_in=solar_panel_in)


@router.delete("/{solar_panel_id}", response_model=SolarPanel)
def delete_solar_panel(
    solar_panel_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a solar panel installation.
    """
    db_solar_panel = crud.solar_panel.get_solar_panel(db, solar_panel_id=solar_panel_id)
    if not db_solar_panel:
        raise HTTPException(status_code=404, detail="SolarPanel not found")
    return crud.solar_panel.delete_solar_panel(db=db, solar_panel_id=solar_panel_id)
