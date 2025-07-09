from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from core.logger_config import setup_logger
from core.security.jwt import create_token, decode_token
from data_base import get_database_session
from models.user import User
from schemas.auth_schemas import CreateRequest
from services import auth_service
from jose import JWTError

logger = setup_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Aktuellen Benutzer anhand des Tokens bekommen
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database_session)) -> User:
    try:
        token_data = decode_token(token)  # Token dekodieren
    except JWTError:
        logger.warning("Ungültiges Token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültiges Token")

    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        logger.warning("Benutzer nicht gefunden")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Benutzer nicht gefunden")
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: CreateRequest, db_session: Session = Depends(get_database_session)):
    logger.info(f"Registrierungsversuch für: {request.email}")
    auth_service.create_user_service(request, db_session)  # Benutzer erstellen
    logger.info("Benutzer erfolgreich erstellt")
    return {"message": "User Created"}


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_database_session)):
    logger.info(f"Login Versuch für Benutzername: {form_data.username}")
    user_obj = auth_service.login_user(form_data.username, form_data.password, db_session)
    if not user_obj:
        logger.warning("Ungültige Anmeldedaten")
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    token = create_token(user_obj.email, user_obj.id, timedelta(minutes=30))  # Token erstellen
    logger.info("Login erfolgreich, Token erstellt")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    logger.info(f"Profilanforderung von Benutzer: {current_user.email}")
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
