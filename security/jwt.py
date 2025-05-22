from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from schemas.auth_schemas import TokenData
from logger_config import setup_logger

logger = setup_logger(__name__)

SECRET_KEY = "secret_key_here"
ALGORITHM = "HS256"

def create_token(email: str, user_id: int, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": email,
        "id": user_id,
        "exp": datetime.utcnow() + expires_delta
    }
    logger.info(f"Token erstellt für Benutzer-ID: {user_id}")

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("Token erfolgreich dekodiert")
    except JWTError:
        logger.warning("Token-Fehler beim Dekodieren")
        raise HTTPException(status_code=401, detail="Ungültiges Token")
    
    email = payload.get("sub")
    user_id = payload.get("id")

    if not email or not user_id:
        logger.warning("Ungültige Token-Daten: E-Mail oder ID fehlt")
        raise HTTPException(status_code=401, detail="Ungültige Token-Daten")

    return TokenData(email=email, id=user_id)






