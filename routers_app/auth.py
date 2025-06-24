from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from schemas.auth_schemas import CreateRequest
from data_base import get_database_session
from services import auth_service
from security import jwt
from datetime import timedelta
from logger_config import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: CreateRequest, db_session: Session = Depends(get_database_session)):
    logger.info(f"Registrierung versuch für: {request.email}")
    auth_service.create_user_service(request, db_session)
    logger.info("Benutzer erfolgreich erstellt")
    return {"message": "User Created"}


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_database_session)):
    logger.info(f"Login Versuch für Benutzername: {form_data.username}")
    user_obj = auth_service.login_user(form_data.username, form_data.password, db_session)
    if not user_obj:
        logger.warning("Ungültige Anmeldedaten")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.create_token(user_obj.email, user_obj.id, timedelta(minutes=30))
    logger.info("Login erfolgreich, Token erstellt")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile")
def get_profile(token: str = Depends(oauth2_scheme)):
    logger.info("Profilanforderung mit Token")
    user_data = jwt.decode_token(token)
    return {"user": user_data}
