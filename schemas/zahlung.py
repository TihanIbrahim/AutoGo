from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# Base model for payment
class ZahlungBase(BaseModel):
    vertragid: int  # Contract ID
    zahlungsmethode: str  # Payment method
    datum: date  # Date of payment
    status: str  # Payment status
    betrag: float  # Amount

    model_config = ConfigDict(from_attributes=True)

# For creating a payment
class ZahlungCreate(ZahlungBase):
    pass

# For updating a payment
class ZahlungUpdate(BaseModel):
    vertragid: Optional[int] = None
    zahlungsmethode: Optional[str] = None
    datum: Optional[date] = None
    status: Optional[str] = None
    betrag: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# For returning payment with ID
class Zahlung(ZahlungBase):
    id: int
