from pydantic import BaseModel

class CreatRequest(BaseModel):
    username:str
    password:str


class tokenDate(BaseModel):
    username:str
    id:int