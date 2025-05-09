from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from schemas.auth_schemas import CreateRequest
from data_base import get_database_Session
from services import auth_service
from security import jwt
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateRequest, db_session: Session = Depends(get_database_Session)):
    auth_service.create_user_service(request, db_session)
    return {"message": "User Created"}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_database_Session)):
    user_obj = auth_service.authenticate_user(form_data.username, form_data.password, db_session)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.create_token(user_obj.username, user_obj.id, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile")
def get_profile(token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode_token(token)
    return {"user": user_data}
