from sqlalchemy.orm import Session
from security.hash import hash_password, verify
from schemas.auth_schemas import CreateRequest
from models.user import User
from fastapi import HTTPException
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def create_user_service(request: CreateRequest, db: Session):
    # Check if user already exists by email
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        logger.warning("Ein Benutzer mit dieser E-Mail existiert bereits.")
        raise HTTPException(status_code=409, detail="Ein Benutzer mit dieser E-Mail existiert bereits.")
    
    # Create a new user with hashed password
    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        role="customer"
    )
    logger.info(f"Benutzer mit E-Mail {request.email} erfolgreich erstellt.")
    
    # Save user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user



def login_user(email: str, password: str, db: Session):
    # Look up user by email
    user_data = db.query(User).filter(User.email == email).first()
    if not user_data:
        logger.warning(f"Anmeldeversuch mit nicht existierender E-Mail: {email}")
        raise HTTPException(status_code=401, detail="Benutzer existiert nicht.")
    
    # Verify the provided password
    if not verify(password, user_data.hashed_password):
        logger.warning(f"Falsches Passwort für Benutzer: {email}")
        raise HTTPException(status_code=401, detail="Falsches Passwort.")

    logger.info(f"Benutzer {email} erfolgreich angemeldet.")
    return user_data

# Function to check if the user has the required role
def check_role(user: User, required_roles: list[str]):
    if user.role not in required_roles:
        raise HTTPException(status_code=403, detail="zugriff verfeigert")
