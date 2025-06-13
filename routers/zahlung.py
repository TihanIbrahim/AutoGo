from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.zahlung import Zahlung as ZahlungModel
from models.vertrag import Vertrag as VertragModel  
from models.user import User
from schemas.zahlung import ZahlungCreate, Zahlung, ZahlungUpdate
from data_base import get_database_session
from logger_config import setup_logger
from services.dependencies import owner_required, owner_or_customer_required, customer_required

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Zahlungen"])


# =================== Create a new payment (Neue Zahlung erstellen) ===================
@router.post("/zahlung", response_model=Zahlung, status_code=201)
def create_zahlung(
    zahlung: ZahlungCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_required)
):
    logger.info(f"Creating new payment for contract ID: {zahlung.vertrag_id}")

    # Validate that amount is not negative
    if zahlung.betrag < 0:
        logger.warning("Invalid amount: Amount cannot be negative.")
        raise HTTPException(status_code=400, detail="Amount cannot be negative.")

    # Check if contract exists
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertrag_id).first()
    if vertrag is None:
        logger.warning(f"Contract with ID {zahlung.vertrag_id} not found.")
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Validate payment date is not before contract start date
    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Invalid payment date: Cannot be before contract start date.")
        raise HTTPException(status_code=400, detail="Payment date cannot be before contract start date.")

    # Create payment record
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
    logger.info(f"Payment successfully created with ID: {db_zahlung.id}")
    return db_zahlung



# =================== List all payments (Alle Zahlungen auflisten) ===================
@router.get("/zahlungen", response_model=List[Zahlung])
def list_zahlungen(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info("Retrieving all payments.")
    zahlungen = db.query(ZahlungModel).all()
    return zahlungen


# =================== Update payment details (Zahlungsdetails aktualisieren) ===================
@router.put("/zahlungen/{zahlung_id}", response_model=Zahlung)
def update_zahlung(
    zahlung_id: int,
    zahlung_update: ZahlungUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_customer_required)
):
    logger.info(f"Updating payment with ID {zahlung_id}.")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if zahlung is None:
        logger.warning(f"Payment with ID {zahlung_id} not found.")
        raise HTTPException(status_code=404, detail=f"Payment with ID {zahlung_id} not found.")

    # Validate amount if provided
    if zahlung_update.betrag is not None and zahlung_update.betrag < 0:
        logger.warning("Invalid amount on update: Amount cannot be negative.")
        raise HTTPException(status_code=400, detail="Amount cannot be negative.")

    # Validate contract if provided
    if zahlung_update.vertrag_id is not None:
        vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung_update.vertrag_id).first()
        if vertrag is None:
            logger.warning(f"Contract with ID {zahlung_update.vertrag_id} not found.")
            raise HTTPException(status_code=404, detail="Contract not found.")
        if zahlung_update.datum is not None and zahlung_update.datum < vertrag.beginnt_datum:
            logger.warning("Invalid payment date on update: Cannot be before contract start date.")
            raise HTTPException(status_code=400, detail="Payment date cannot be before contract start date.")

    # Apply updates
    if zahlung_update.vertrag_id is not None:
        zahlung.vertrag_id = zahlung_update.vertrag_id
    if zahlung_update.zahlungsmethode is not None:
        zahlung.zahlungsmethode = zahlung_update.zahlungsmethode
    if zahlung_update.datum is not None:
        zahlung.datum = zahlung_update.datum
    if zahlung_update.status is not None:
        zahlung.status = zahlung_update.status
    if zahlung_update.betrag is not None:
        zahlung.betrag = zahlung_update.betrag

    db.commit()
    db.refresh(zahlung)
    logger.info(f"Payment with ID {zahlung_id} successfully updated.")
    return zahlung



# =================== Delete a payment (Zahlung löschen) ===================
@router.delete("/zahlungen/{zahlung_id}", status_code=204)
def delete_zahlung(
    zahlung_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Attempting to delete payment with ID {zahlung_id}.")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if zahlung is None:
        logger.warning(f"Payment with ID {zahlung_id} not found.")
        raise HTTPException(status_code=404, detail="Payment not found.")

    # Delete payment record
    db.delete(zahlung)
    db.commit()
    logger.info(f"Payment with ID {zahlung_id} successfully deleted.")
    return

