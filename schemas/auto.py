from pydantic import BaseModel,ConfigDict

class AutoBase(BaseModel):
    brand: str
    model: str
    jahr: int
    preis_pro_stunde: int
    status: bool

    class Config(ConfigDict):  
        from_attributes = True

class AutoCreate(AutoBase):
    pass

class Auto(AutoBase):
    id: int

    class Config(ConfigDict):  
        from_attributes = True



