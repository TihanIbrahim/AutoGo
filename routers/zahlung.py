from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.zahlung import Zahlung as ZahlungModel
from models.vertrag import Vertrag as VertragModel  
from models.user import User
from schemas.zahlung import ZahlungCreate, Zahlung, ZahlungUpdate
from data_base import get_database_session
from logger_config import setup_logger
from services.dependencies import owner_required, owner_or_customer_required ,customer_required
from datetime import datetime

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Zahlungen"])


@router.post("/zahlung", response_model=Zahlung, status_code=201)
def create_zahlung(
    zahlung: ZahlungCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_required)

):
    logger.info(f"Creating new payment for contract ID: {zahlung.vertragid}")

    # Validate that amount is not negative
    if zahlung.betrag < 0:
        logger.warning("Invalid amount: amount cannot be negative.")
        raise HTTPException(status_code=400, detail="Amount cannot be negative.")

    # Check if contract exists
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertragid).first()
    if not vertrag:
        logger.warning(f"Contract with ID {zahlung.vertragid} not found.")
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Validate payment date is not before contract start date
    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Invalid payment date: cannot be before contract start.")
        raise HTTPException(status_code=400, detail="Payment date cannot be before contract start date.")

    # Create payment record
    db_zahlung = ZahlungModel(
        vertragid=zahlung.vertragid,
        zahlungsmethode=zahlung.zahlungsmethode,
        datum=zahlung.datum,
        status=zahlung.status,
        betrag=zahlung.betrag
    )
    db.add(db_zahlung)
    db.commit()
    db.refresh(db_zahlung)
    logger.info(f"Payment created successfully with ID: {db_zahlung.id}")
    return db_zahlung


@router.get("/zahlungen", response_model=List[Zahlung])
def list_zahlungen(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  
):
    logger.info("Fetching all payments")
    zahlungen = db.query(ZahlungModel).all()
    if not zahlungen:
        logger.warning("No payments found")
        raise HTTPException(status_code=404, detail="No payments found.")
    return zahlungen


@router.put("/zahlungen/{zahlung_id}", response_model=Zahlung)
def update_zahlung(
    zahlung_id: int,
    zahlung_update: ZahlungUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_customer_required) 
):
    logger.info(f"Updating payment with ID {zahlung_id}")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Payment with ID {zahlung_id} not found")
        raise HTTPException(status_code=404, detail=f"Payment with ID {zahlung_id} not found.")

    # Validate that amount is not negative
    if zahlung_update.betrag < 0:
        logger.warning("Invalid amount in update: amount cannot be negative.")
        raise HTTPException(status_code=400, detail="Amount cannot be negative.")

    # Check if contract exists
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung_update.vertragid).first()
    if not vertrag:
        logger.warning(f"Contract with ID {zahlung_update.vertragid} not found.")
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Validate payment date is not before contract start date
    if zahlung_update.datum < vertrag.beginnt_datum:
        logger.warning("Invalid payment date in update: cannot be before contract start.")
        raise HTTPException(status_code=400, detail="Payment date cannot be before contract start date.")

    # Update payment data
    zahlung.vertragid = zahlung_update.vertragid
    zahlung.zahlungsmethode = zahlung_update.zahlungsmethode
    zahlung.datum = zahlung_update.datum
    zahlung.status = zahlung_update.status
    zahlung.betrag = zahlung_update.betrag

    db.commit()
    db.refresh(zahlung)
    logger.info(f"Payment with ID {zahlung_id} updated successfully")
    return zahlung


@router.delete("/zahlungen/{zahlung_id}", status_code=204)
def delete_zahlung(
    zahlung_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  
):
    logger.info(f"Attempting to delete payment with ID {zahlung_id}")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Payment with ID {zahlung_id} not found")
        raise HTTPException(status_code=404, detail="Payment not found")

    # Delete payment record
    db.delete(zahlung)
    db.commit()
    logger.info(f"Payment with ID {zahlung_id} deleted successfully")
    return  # 204 No Content: no response body returned
