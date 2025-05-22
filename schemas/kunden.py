from pydantic import BaseModel, EmailStr, ConfigDict  
from datetime import date
from typing import Optional

# Base class for Kunden schema with required fields
class KundenBase(BaseModel):
    vorname: str  # First name
    nachname: str  # Last name
    geb_datum: date  # Date of birth
    handy_nummer: str  # Phone number
    email: EmailStr  # Email address

    model_config = ConfigDict(from_attributes=True)  # Parse data from attributes

# Model for creating a new Kunden
class KundenCreate(KundenBase):
    pass

# Model for Kunden with ID
class Kunden(KundenBase):
    id: int  # Unique identifier for the customer

    model_config = ConfigDict(from_attributes=True)

# Model for updating an existing Kunden, all fields are optional
class KundenUpdate(BaseModel):
    vorname: Optional[str] = None  # Optional first name
    nachname: Optional[str] = None  # Optional last name
    geb_datum: Optional[date] = None  # Optional date of birth
    handy_nummer: Optional[str] = None  # Optional phone number
    email: Optional[EmailStr] = None  # Optional email address

    model_config = ConfigDict(from_attributes=True)


