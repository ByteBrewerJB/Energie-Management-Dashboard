from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .car import CarChargeCreate, CarChargeRead


class MonthlyJournalBase(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    consumption_tariff_1_kwh: Optional[float] = None
    consumption_tariff_2_kwh: Optional[float] = None
    feed_in_without_battery_kwh: Optional[float] = None
    total_house_consumption_kwh: Optional[float] = None
    avg_consumption_tariff_low_eur_kwh: Optional[float] = None
    avg_consumption_tariff_high_eur_kwh: Optional[float] = None
    supplier_costs_eur: Optional[float] = None
    avg_feed_in_tariff_eur_kwh: Optional[float] = None
    solar_production_kwh: Optional[float] = None
    battery_charge_kwh: Optional[float] = None
    battery_discharge_kwh: Optional[float] = None
    advance_payment_eur: Optional[float] = None


class MonthlyJournalCreate(MonthlyJournalBase):
    car_charges: List[CarChargeCreate] = Field(default_factory=list)


class MonthlyJournalUpdate(BaseModel):
    consumption_tariff_1_kwh: Optional[float] = None
    consumption_tariff_2_kwh: Optional[float] = None
    feed_in_without_battery_kwh: Optional[float] = None
    total_house_consumption_kwh: Optional[float] = None
    avg_consumption_tariff_low_eur_kwh: Optional[float] = None
    avg_consumption_tariff_high_eur_kwh: Optional[float] = None
    supplier_costs_eur: Optional[float] = None
    avg_feed_in_tariff_eur_kwh: Optional[float] = None
    solar_production_kwh: Optional[float] = None
    battery_charge_kwh: Optional[float] = None
    battery_discharge_kwh: Optional[float] = None
    advance_payment_eur: Optional[float] = None
    car_charges: Optional[List[CarChargeCreate]] = None


class MonthlyJournalRead(MonthlyJournalBase):
    id: int
    car_charges: List[CarChargeRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
