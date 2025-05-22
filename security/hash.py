from logger_config import setup_logger
from passlib.context import CryptContext

# Logger konfigurieren
logger = setup_logger(__name__)

# Passwort-Kontext für Hashing konfigurieren
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    hashed = pwd_context.hash(password)
    logger.info("Passwort erfolgreich gehasht.")  
    return hashed

def verify(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logger.info("Passwortüberprüfung erfolgreich.")
    else:
        logger.warning("Passwortüberprüfung fehlgeschlagen.")
    return result
