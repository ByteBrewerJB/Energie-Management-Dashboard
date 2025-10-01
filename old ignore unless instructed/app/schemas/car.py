from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

# Shared properties
class CarBase(BaseModel):
    name: Optional[str] = None
    reimbursement_rate_eur_per_kwh: Optional[Decimal] = None


# Properties to receive on item creation
class CarCreate(CarBase):
    name: str
    reimbursement_rate_eur_per_kwh: Decimal


# Properties to receive on item update
class CarUpdate(CarBase):
    pass


# Properties shared by models stored in DB
class CarInDBBase(CarBase):
    id: int
    name: str
    reimbursement_rate_eur_per_kwh: Decimal

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class Car(CarInDBBase):
    pass
