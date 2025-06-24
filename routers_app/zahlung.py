from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.zahlung import Zahlung as ZahlungModel
from models.vertrag import Vertrag as VertragModel  
from models.user import User
from schemas.zahlung import ZahlungCreate, Zahlung
from data_base import get_database_session
from logger_config import setup_logger
from services.dependencies import customer_or_guest_required

# Initialize the logger for this module
logger = setup_logger(__name__)

# Define the API router for payment-related endpoints
router = APIRouter(prefix="/api/v1")

# =================== Create a new payment ===================
@router.post("/zahlungen", response_model=Zahlung, status_code=201)
def create_zahlung(
    zahlung: ZahlungCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_or_guest_required)
):
    # Log the creation attempt
    logger.info(f"Creating new payment for contract ID: {zahlung.vertrag_id}")

    # Validate that the payment amount is not negative
    if zahlung.betrag < 0:
        logger.warning("Invalid amount: Amount cannot be negative.")
        raise HTTPException(status_code=400, detail="Amount cannot be negative.")

    # Check if the related contract exists in the database
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertrag_id).first()
    if vertrag is None:
        logger.warning(f"Contract with ID {zahlung.vertrag_id} not found.")
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Validate that the payment date is not before the contract start date
    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Invalid payment date: Cannot be before contract start date.")
        raise HTTPException(status_code=400, detail="Payment date cannot be before contract start date.")

    # Create the payment entry in the database
    db_zahlung = ZahlungModel(
        vertrag_id=zahlung.vertrag_id,
        zahlungsmethode=zahlung.zahlungsmethode,
        datum=zahlung.datum,
        status=zahlung.status,
        betrag=zahlung.betrag
    )
    db.add(db_zahlung)
    db.commit()
    db.refresh(db_zahlung)

    # Log success
    logger.info(f"Payment successfully created with ID: {db_zahlung.id}")
    
    return db_zahlung
