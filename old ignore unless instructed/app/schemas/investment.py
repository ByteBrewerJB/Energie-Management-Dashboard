from pydantic import BaseModel, Field
from typing import Union, Literal
from datetime import date
from decimal import Decimal

# Re-defining the creation schemas with a 'type' literal for discriminated union
class SolarPanelInvestmentCreate(BaseModel):
    type: Literal['solar_panel']
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    total_power_wp: int
    expected_annual_yield_kwh: int | None = None

class BatteryInvestmentCreate(BaseModel):
    type: Literal['battery']
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    # Per user request, brand and capacity are not included in the create form for now
    # brand: str | None = None
    # capacity_kwh: float

# A union of all possible investment creation models
InvestmentCreate = Union[SolarPanelInvestmentCreate, BatteryInvestmentCreate]


# Re-defining the full schemas for response models, including the 'type' literal
class SolarPanelInvestment(BaseModel):
    id: int
    type: Literal['solar_panel'] = 'solar_panel'
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    total_power_wp: int
    expected_annual_yield_kwh: int | None = None

    class Config:
        from_attributes = True

class BatteryInvestment(BaseModel):
    id: int
    type: Literal['battery'] = 'battery'
    name: str
    purchase_date: date
    purchase_cost_eur: Decimal
    brand: str | None = None
    capacity_kwh: float

    class Config:
        from_attributes = True

# A union of all possible investment response models
Investment = Union[SolarPanelInvestment, BatteryInvestment]
