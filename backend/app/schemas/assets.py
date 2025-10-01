from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SolarPanelInstallationBase(BaseModel):
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[float] = None
    total_power_wp: Optional[int] = None
    expected_annual_yield_kwh: Optional[int] = None


class SolarPanelInstallationCreate(SolarPanelInstallationBase):
    pass


class SolarPanelInstallationUpdate(SolarPanelInstallationBase):
    pass


class SolarPanelInstallationRead(SolarPanelInstallationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BatteryBase(BaseModel):
    purchase_date: Optional[date] = None
    purchase_cost_eur: Optional[float] = None
    capacity_kwh: Optional[float] = None
    brand_model: Optional[str] = None


class BatteryCreate(BatteryBase):
    pass


class BatteryUpdate(BatteryBase):
    pass


class BatteryRead(BatteryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
