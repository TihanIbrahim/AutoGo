from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from schemas.auth_schemas import TokenData

# إعدادات JWT
SECRET_KEY = "secret_key_here"
ALGORITHM = "HS256"

# دالة لإنشاء توكن JWT
def create_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": username,
        "id": user_id,
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# دالة لفك التوكن والتحقق من صحته
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    user_id = payload.get("id")

    if not username or not user_id:
        raise HTTPException(status_code=401, detail="Invalid token data")

    return TokenData(username=username, id=user_id)

