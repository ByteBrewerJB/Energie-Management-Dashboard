from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.api import deps
from app.schemas.investment import Investment, InvestmentCreate, SolarPanelInvestment, BatteryInvestment
from app.schemas.solar_panel import SolarPanelUpdate
from app.schemas.battery import BatteryUpdate
from app.crud import crud_solar_panel, crud_battery
from app.models.models import SolarPanel, Battery

router = APIRouter()


@router.get("/investments", response_model=List[Investment])
def read_investments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all solar panel and battery installations (investments).
    """
    solar_panels = crud_solar_panel.get_multi(db, skip=skip, limit=limit)
    batteries = crud_battery.get_multi(db, skip=skip, limit=limit)

    # Add a 'type' attribute to each object before returning
    # Pydantic will use this for the discriminated union
    all_investments = [
        SolarPanelInvestment.from_orm(p) for p in solar_panels
    ] + [
        BatteryInvestment.from_orm(b) for b in batteries
    ]

    # Sort by purchase date
    all_investments.sort(key=lambda x: x.purchase_date, reverse=True)

    return all_investments


@router.post("/investments", response_model=Investment, status_code=status.HTTP_201_CREATED)
def create_investment(
    *,
    db: Session = Depends(get_db),
    investment_in: InvestmentCreate,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new investment (either solar panel or battery).
    """
    if investment_in.type == 'solar_panel':
        investment = crud_solar_panel.create(db=db, obj_in=investment_in)
        return SolarPanelInvestment.from_orm(investment)
    elif investment_in.type == 'battery':
        investment = crud_battery.create(db=db, obj_in=investment_in)
        return BatteryInvestment.from_orm(investment)
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


@router.get("/investments/{item_type}/{item_id}", response_model=Investment)
def read_investment(
    *,
    db: Session = Depends(get_db),
    item_type: str,
    item_id: int,
) -> Any:
    """
    Get a specific investment by its type and ID.
    """
    if item_type == "solar_panel":
        investment = crud_solar_panel.get(db, solar_panel_id=item_id)
        if not investment:
            raise HTTPException(status_code=404, detail="Solar panel not found")
        return SolarPanelInvestment.from_orm(investment)
    elif item_type == "battery":
        investment = crud_battery.get(db, battery_id=item_id)
        if not investment:
            raise HTTPException(status_code=404, detail="Battery not found")
        return BatteryInvestment.from_orm(investment)
    else:
        raise HTTPException(status_code=404, detail="Investment type not found")


@router.put("/investments/{item_type}/{item_id}", response_model=Investment)
def update_investment(
    *,
    db: Session = Depends(get_db),
    item_type: str,
    item_id: int,
    investment_in: dict,  # Using a generic dict to handle different update schemas
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing investment.
    """
    if item_type == "solar_panel":
        investment = crud_solar_panel.get(db, solar_panel_id=item_id)
        if not investment:
            raise HTTPException(status_code=404, detail="Solar panel not found")
        update_schema = SolarPanelUpdate(**investment_in)
        updated_investment = crud_solar_panel.update(db=db, db_obj=investment, obj_in=update_schema)
        return SolarPanelInvestment.from_orm(updated_investment)
    elif item_type == "battery":
        investment = crud_battery.get(db, battery_id=item_id)
        if not investment:
            raise HTTPException(status_code=404, detail="Battery not found")
        update_schema = BatteryUpdate(**investment_in)
        updated_investment = crud_battery.update(db=db, db_obj=investment, obj_in=update_schema)
        return BatteryInvestment.from_orm(updated_investment)
    else:
        raise HTTPException(status_code=404, detail="Investment type not found")


@router.delete("/investments/{item_type}/{item_id}", response_model=Investment)
def delete_investment(
    *,
    db: Session = Depends(get_db),
    item_type: str,
    item_id: int,
    current_user: str = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an investment.
    """
    if item_type == "solar_panel":
        investment = crud_solar_panel.get(db, solar_panel_id=item_id)
        if not investment:
            raise HTTPException(status_code=404, detail="Solar panel not found")
        deleted_investment = crud_solar_panel.remove(db=db, solar_panel_id=item_id)
        return SolarPanelInvestment.from_orm(deleted_investment)
    elif item_type == "battery":
        investment = crud_battery.get(db, battery_id=item_id)
        if not investment:
            raise HTTPException(status_code=404, detail="Battery not found")
        deleted_investment = crud_battery.remove(db=db, battery_id=item_id)
        return BatteryInvestment.from_orm(deleted_investment)
    else:
        raise HTTPException(status_code=404, detail="Investment type not found")
