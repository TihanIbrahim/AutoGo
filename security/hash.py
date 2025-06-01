from logger_config import setup_logger
from passlib.context import CryptContext

# Set up logger
logger = setup_logger(__name__)

# Configure password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def hash_password(password: str) -> str:
    hashed = pwd_context.hash(password)
    logger.info("Password hashed successfully.")
    return hashed

# Function to verify a plain password against a hashed one
def verify(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logger.info("Password verification successful.")
    else:
        logger.warning("Password verification failed.")
    return result
