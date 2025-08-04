from core.logger_config import setup_logger
from passlib.context import CryptContext

# Logger für dieses Modul einrichten
logger = setup_logger(__name__)

# Konfiguration des Passwort-Hashing-Kontexts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funktion zum Hashen eines Passworts
def hash_password(password: str) -> str:
    hashed = pwd_context.hash(password)
    logger.info("Passwort wurde erfolgreich gehasht.")
    return hashed

# Funktion zur Überprüfung eines Klartext-Passworts mit einem gehashten Passwort
def verify(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logger.info("Passwortüberprüfung erfolgreich.")
    else:
        logger.warning("Passwortüberprüfung fehlgeschlagen.")
    return result
