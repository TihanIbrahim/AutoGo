from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from data_base import get_database_session
from security import jwt
from models.user import User

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database_session)) -> User:
    try:
        # Decode the token to extract user info
        token_data = jwt.decode_token(token)
    except:
        # Raise error if token is invalid
        raise HTTPException(status_code=401, detail="Ungültiges Token")  

    email = token_data.email

    # Look up the user in the database by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Raise error if user not found
        raise HTTPException(status_code=401, detail="Benutzer wurde nicht gefunden") 

    return user
