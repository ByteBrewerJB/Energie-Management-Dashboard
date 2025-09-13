from pydantic import BaseModel
from typing import Optional

class CarBase(BaseModel):
    name: str
    reimbursement_rate_eur_per_kwh: float

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    name: Optional[str] = None
    reimbursement_rate_eur_per_kwh: Optional[float] = None

class Car(CarBase):
    id: int

    class Config:
        from_attributes = True
