from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.auth_schemas import CreateRequest  
from services.auth_service import create_user_service, login_user  
from data_base import get_database_Session
from logger_config import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: CreateRequest, db: Session = Depends(get_database_Session)):
    logger.info(f"Attempting registration for email: {request.email}")
    try:
        create_user_service(request, db)
        logger.info(f"User successfully created: {request.email}")
        return {"message": "User successfully registered"}
    except ValueError:
        logger.warning(f"Registration failed: Email already registered {request.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception:
        logger.error(f"Internal server error during registration for {request.email}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

@router.post("/login")
def login(request: CreateRequest, db: Session = Depends(get_database_Session)):
    logger.info(f"Login attempt for email: {request.email}")
    try:
        user = login_user(request.email, request.password, db)
        if not user:
            logger.warning(f"Login failed: Invalid credentials for {request.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        logger.info(f"Login successful for {request.email}")
        return {"message": "Login successful"}
    except Exception:
        logger.error(f"Error during login for {request.email}")
        raise HTTPException(status_code=500, detail="Error during login")
