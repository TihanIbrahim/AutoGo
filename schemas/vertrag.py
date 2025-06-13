from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from enum import Enum

class VertragStatus(str, Enum):
    aktiv = "aktiv"
    beendet = "beendet"
    gekündigt = "gekündigt"

# Base model for rental contract with required and optional fields
class VertragBase(BaseModel):
    auto_id: int                  # Car ID
    kunden_id: int                # Customer ID
    beginnt_datum: date           # Contract start date
    beendet_datum: Optional[date] = None   # Contract end date (optional)
    status: VertragStatus
    total_preis: Optional[float] = None    # Total price (optional)

    model_config = ConfigDict(from_attributes=True)

# Model for creating a new contract (inherits all fields)
class VertragCreate(VertragBase):
    pass

# Model for updating an existing contract, all fields optional
class VertragUpdate(BaseModel):
    auto_id: Optional[int] = None
    kunden_id: Optional[int] = None
    beginnt_datum: Optional[date] = None
    beendet_datum: Optional[date] = None
    status: Optional[VertragStatus] = None
    total_preis: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# Model representing a contract including its ID
class Vertrag(VertragBase):
    id: int  # Contract ID (Primary Key)
