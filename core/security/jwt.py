from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from schemas.auth_schemas import TokenData
from core.logger_config import setup_logger
from core.config import SECRET_KEY, ALGORITHM

# Set up logger
logger = setup_logger(__name__)

# Function to create a JWT token
def create_token(email: str, user_id: int, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": email,
        "id": user_id,
        "exp": datetime.utcnow() + expires_delta
    }
    logger.info(f"Token created for user ID: {user_id}")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to decode a JWT token
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("Token successfully decoded")
    except JWTError:
        logger.warning("Token decoding failed")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user_id = payload.get("id")

    if not email or not user_id:
        logger.warning("Invalid token data: missing email or ID")
        raise HTTPException(status_code=401, detail="Invalid token data")

    return TokenData(email=email, id=user_id)

