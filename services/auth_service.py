from sqlalchemy.orm import Session
from security.hash import hash_password,verify
from schemas.auth_schemas import CreatRequest
from models import user

def creat_user(request:CreatRequest , db: Session):
    neu_user=user.User(
        username=request.username,
        hashed_password=hash_password(request.password)

       
    )
    db.add(neu_user)
    db.commit()

def login(username:str , password:str,db:Session):
    user_Data=db.query(user.User).filter(user.User.username==username).first()
    if user_Data and verify(password,user_Data.hashed_password):
        return user_Data
    return None 