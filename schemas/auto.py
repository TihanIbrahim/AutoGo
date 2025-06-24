from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum

# Enum for car status
class AutoStatus(str, Enum):
    verfügbar = "verfügbar"       # available
    reserviert = "reserviert"     # reserved
    vermietet = "vermietet"       # renteda
    in_wartung = "in_wartung"     # under maintenance
    beschädigt = "beschädigt"     # damaged
    außer_betrieb = "außer_betrieb"  # out of service

# Base schema for Auto with common fields
class AutoBase(BaseModel):
    brand: str
    model: str
    jahr: int
    preis_pro_stunde: float
    status: AutoStatus

    model_config = ConfigDict(from_attributes=True)

# Schema for creating an Auto (inherits from AutoBase)
class AutoCreate(AutoBase):
    pass

# Schema for updating an Auto (all fields optional)
class AutoUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    jahr: Optional[int] = None
    preis_pro_stunde: Optional[float] = None
    status: Optional[AutoStatus] = None

    model_config = ConfigDict(from_attributes=True)

# Schema including the ID (for read operations)
class Auto(AutoBase):
    id: int
