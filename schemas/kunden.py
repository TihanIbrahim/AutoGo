from pydantic import BaseModel, EmailStr,ConfigDict  
from datetime import date

class KundenBase(BaseModel):
    vorname: str
    nachname: str
    geb_datum: date
    handy_nummer: str
    email: EmailStr 

    
    class Config(ConfigDict):  
        from_attributes = True

class KundenCreate(KundenBase):
    pass

class Kunden(KundenBase):
    id: int

   
    class Config(ConfigDict):  
        from_attributes = True
