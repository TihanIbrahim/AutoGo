from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from data_base import get_database_Session

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
def register_user(email: str, password: str, db_session: Session = Depends(get_database_Session)):
    hashed_password = pwd_context.hash(password)
    user = User(email=email, password=hashed_password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {"message": "User created"}

@router.post("/login")
def login_user(email: str, password: str, db_session: Session = Depends(get_database_Session)):
    user = db_session.query(User).filter(User.email == email).first()

    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Email oder Passwort falsch.")

    return {"message": "Login erfolgreich ✅"}
