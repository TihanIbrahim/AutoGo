from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from enum import Enum


class ZahlungsmethodeEnum(str, Enum):
    karte = "karte"
    überweisung = "überweisung"
    paypal = "paypal"
    stripe = "stripe"
    klarna = "klarna"


class ZahlungsStatusEnum(str, Enum):
    bezahlt = "bezahlt"
    offen = "offen"
    abgebrochen = "abgebrochen"
    teilweise = "teilweise"
    zurückerstattet = "zurückerstattet"


class ZahlungBase(BaseModel):
    vertrag_id: int                 # Contract ID
    zahlungsmethode: ZahlungsmethodeEnum  # Payment method
    datum: date                    # Payment date
    status: ZahlungsStatusEnum     # Payment status
    betrag: float                  # Amount

    model_config = ConfigDict(from_attributes=True)


class ZahlungCreate(ZahlungBase):
    pass  # For creating a payment


class ZahlungUpdate(BaseModel):
    vertrag_id: Optional[int] = None
    zahlungsmethode: Optional[ZahlungsmethodeEnum] = None
    datum: Optional[date] = None
    status: Optional[ZahlungsStatusEnum] = None
    betrag: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class Zahlung(ZahlungBase):
    id: int  # Payment ID

