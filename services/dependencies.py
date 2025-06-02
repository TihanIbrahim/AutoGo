from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from data_base import get_database_session
from security import jwt
from models.user import User
from services.auth_service import check_role

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


def role_required(allowed_roles: list[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied: insufficient role")
        return current_user
    return dependency


owner_required = role_required(["owner"])
customer_required = role_required(["customer"])
owner_or_customer_required = role_required(["owner", "customer"])