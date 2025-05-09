from pydantic import BaseModel,ConfigDict  
from datetime import date

class VertragBase(BaseModel):
    auto_id: int
    kunden_id: int
    beginnt_datum: date
    beendet_datum: date
    total_prise: float
    status : bool

    class Config(ConfigDict):  
        from_attributes = True

class VertragCreate(VertragBase):
    pass

class Vertrag(VertragBase):
    id: int  

    class Config:
        from_attributes = True
