from typing import Optional

from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    name: str
    reimbursement_rate_ex_vat_eur_kwh: Optional[float] = None
    reimbursement_rate_inc_vat_eur_kwh: Optional[float] = None
    is_active: bool = True


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    name: Optional[str] = None
    reimbursement_rate_ex_vat_eur_kwh: Optional[float] = None
    reimbursement_rate_inc_vat_eur_kwh: Optional[float] = None
    is_active: Optional[bool] = None


class CarRead(CarBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CarChargeBase(BaseModel):
    car_id: int
    charged_kwh: float


class CarChargeCreate(CarChargeBase):
    pass


class CarChargeUpdate(BaseModel):
    charged_kwh: Optional[float] = None


class CarChargeRead(CarChargeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
