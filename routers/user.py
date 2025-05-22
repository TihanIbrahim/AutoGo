from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.auth_schemas import CreateRequest  
from services.auth_service import create_user_service, login_user  
from data_base import get_database_Session
from logger_config import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: CreateRequest, db: Session = Depends(get_database_Session)):
    logger.info(f"Registrierung versucht für E-Mail: {request.email}")
    try:
        user = create_user_service(request, db)
        logger.info(f"Benutzer erfolgreich erstellt: {request.email}")
        return {"message": "Benutzer wurde erfolgreich erstellt"}
    except ValueError:
        logger.warning(f"Registrierung fehlgeschlagen: E-Mail bereits registriert {request.email}")
        raise HTTPException(status_code=400, detail="E-Mail ist bereits registriert")
    except Exception:
        logger.error(f"Interner Serverfehler bei Registrierung für {request.email}")
        raise HTTPException(status_code=500, detail="Interner Serverfehler beim Registrieren")

@router.post("/login")
def login(request: CreateRequest, db: Session = Depends(get_database_Session)):
    logger.info(f"Login versucht für E-Mail: {request.email}")
    try:
        user = login_user(request.email, request.password, db)
        if not user:
            logger.warning(f"Login fehlgeschlagen: Ungültige Daten für {request.email}")
            raise HTTPException(status_code=401, detail="Ungültige E-Mail oder Passwort")
        logger.info(f"Login erfolgreich für {request.email}")
        return {"message": "Login erfolgreich"}
    except Exception:
        logger.error(f"Fehler beim Anmelden für {request.email}")
        raise HTTPException(status_code=500, detail="Fehler beim Anmelden")
