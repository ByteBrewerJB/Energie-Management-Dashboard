from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.solar_panel import SolarPanel, SolarPanelCreate, SolarPanelUpdate
from app.crud import crud_solar_panel

router = APIRouter()

@router.get("/solar_panels", response_model=List[SolarPanel])
def read_solar_panels(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all solar panel installations.
    """
    solar_panels = crud_solar_panel.get_multi(db, skip=skip, limit=limit)
    return solar_panels


@router.post("/solar_panels", response_model=SolarPanel, status_code=status.HTTP_201_CREATED)
def create_solar_panel(
    *,
    db: Session = Depends(get_db),
    solar_panel_in: SolarPanelCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new solar panel installation.
    """
    solar_panel = crud_solar_panel.create(db=db, obj_in=solar_panel_in)
    return solar_panel


@router.get("/solar_panels/{solar_panel_id}", response_model=SolarPanel)
def read_solar_panel(
    *,
    db: Session = Depends(get_db),
    solar_panel_id: int,
) -> Any:
    """
    Get a specific solar panel installation by its ID.
    """
    solar_panel = crud_solar_panel.get(db, solar_panel_id=solar_panel_id)
    if not solar_panel:
        raise HTTPException(status_code=404, detail="Solar panel installation not found")
    return solar_panel


@router.put("/solar_panels/{solar_panel_id}", response_model=SolarPanel)
def update_solar_panel(
    *,
    db: Session = Depends(get_db),
    solar_panel_id: int,
    solar_panel_in: SolarPanelUpdate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing solar panel installation.
    """
    solar_panel = crud_solar_panel.get(db, solar_panel_id=solar_panel_id)
    if not solar_panel:
        raise HTTPException(status_code=404, detail="Solar panel installation not found")

    solar_panel = crud_solar_panel.update(db=db, db_obj=solar_panel, obj_in=solar_panel_in)
    return solar_panel


@router.delete("/solar_panels/{solar_panel_id}", response_model=SolarPanel)
def delete_solar_panel(
    *,
    db: Session = Depends(get_db),
    solar_panel_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a solar panel installation.
    """
    solar_panel = crud_solar_panel.get(db, solar_panel_id=solar_panel_id)
    if not solar_panel:
        raise HTTPException(status_code=404, detail="Solar panel installation not found")

    solar_panel = crud_solar_panel.remove(db=db, solar_panel_id=solar_panel_id)
    return solar_panel
