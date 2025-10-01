from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, get_db_session
from ..models.assets import Battery, SolarPanelInstallation
from ..models.user import User
from ..schemas.assets import (
    BatteryCreate,
    BatteryRead,
    BatteryUpdate,
    SolarPanelInstallationCreate,
    SolarPanelInstallationRead,
    SolarPanelInstallationUpdate,
)

router = APIRouter()


@router.get("/solar", response_model=Optional[SolarPanelInstallationRead])
def get_solar_installation(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Optional[SolarPanelInstallation]:
    return (
        db.query(SolarPanelInstallation)
        .filter(SolarPanelInstallation.owner_id == current_user.id)
        .first()
    )


@router.put("/solar", response_model=SolarPanelInstallationRead)
def upsert_solar_installation(
    body: SolarPanelInstallationUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> SolarPanelInstallation:
    installation = (
        db.query(SolarPanelInstallation)
        .filter(SolarPanelInstallation.owner_id == current_user.id)
        .first()
    )
    if not installation:
        installation = SolarPanelInstallation(owner_id=current_user.id)
        db.add(installation)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(installation, field, value)

    db.commit()
    db.refresh(installation)
    return installation


@router.get("/battery", response_model=Optional[BatteryRead])
def get_battery(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Optional[Battery]:
    return db.query(Battery).filter(Battery.owner_id == current_user.id).first()


@router.put("/battery", response_model=BatteryRead)
def upsert_battery(
    body: BatteryUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Battery:
    battery = db.query(Battery).filter(Battery.owner_id == current_user.id).first()
    if not battery:
        battery = Battery(owner_id=current_user.id)
        db.add(battery)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(battery, field, value)

    db.commit()
    db.refresh(battery)
    return battery


@router.delete("/battery", status_code=status.HTTP_204_NO_CONTENT)
def delete_battery(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    battery = db.query(Battery).filter(Battery.owner_id == current_user.id).first()
    if battery:
        db.delete(battery)
        db.commit()


@router.delete("/solar", status_code=status.HTTP_204_NO_CONTENT)
def delete_solar_installation(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    installation = (
        db.query(SolarPanelInstallation)
        .filter(SolarPanelInstallation.owner_id == current_user.id)
        .first()
    )
    if installation:
        db.delete(installation)
        db.commit()
