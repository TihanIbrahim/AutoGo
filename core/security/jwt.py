from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from schemas.auth_schemas import TokenData
from core.logger_config import setup_logger
from core.config import SECRET_KEY, ALGORITHM

# Logger einrichten
logger = setup_logger(__name__)

# Funktion zum Erstellen eines JWT-Tokens
def create_token(email: str, user_id: int, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": email,     # E-Mail als "subject" im Token speichern
        "id": user_id,    # Benutzer-ID speichern
        "exp": datetime.utcnow() + expires_delta  # Ablaufdatum berechnen
    }
    logger.info(f"Token für Benutzer-ID {user_id} erstellt")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Token erstellen und zurückgeben

# Funktion zum Entschlüsseln eines JWT-Tokens
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Token dekodieren
        logger.info("Token erfolgreich dekodiert")
    except JWTError:
        logger.warning("Fehler beim Dekodieren des Tokens")
        raise HTTPException(status_code=401, detail="Ungültiges Token")  # Fehler bei ungültigem Token
    
    email = payload.get("sub")     # E-Mail extrahieren
    user_id = payload.get("id")    # Benutzer-ID extrahieren

    if not email or not user_id:
        logger.warning("Ungültige Token-Daten: E-Mail oder ID fehlt")
        raise HTTPException(status_code=401, detail="Ungültige Token-Daten")

    return TokenData(email=email, id=user_id)  # Token-Daten als Objekt zurückgeben