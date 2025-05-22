from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class ZahlungBase(BaseModel):
    vertragid: int 
    zahlungsmethode: str 
    datum: date
    status: str
    betrag: float

    model_config = ConfigDict(from_attributes=True)

class ZahlungCreate(ZahlungBase):
    pass


class ZahlungUpdate(BaseModel):
    vertragid: Optional[int] = None
    zahlungsmethode: Optional[str] = None
    datum: Optional[date] = None
    status: Optional[str] = None
    betrag: Optional[float] = None
    
    
    model_config = ConfigDict(from_attributes=True) 

class Zahlung(ZahlungBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


