from pydantic import BaseModel, ConfigDict
from typing import Optional

# Base class for Auto models with common attributes
class AutoBase(BaseModel):
    brand: str  # Car brand
    model: str  # Car model
    jahr: int  # Manufacture year
    preis_pro_stunde: int  # Hourly rental price
    status: bool  # Car availability status

    model_config = ConfigDict(from_attributes=True)  # Parse data from attributes

# Model for creating a new Auto
class AutoCreate(AutoBase):
    pass

# Model for Auto with ID
class Auto(AutoBase):
    id: int  # Car ID

# Model for updating an existing Auto
class AutoUpdate(BaseModel):
    brand: Optional[str] = None  # Optional update for brand
    model: Optional[str] = None  # Optional update for model
    jahr: Optional[int] = None  # Optional update for year
    preis_pro_stunde: Optional[int] = None  # Optional update for price
    status: Optional[bool] = None  # Optional update for status

    model_config = ConfigDict(from_attributes=True)
