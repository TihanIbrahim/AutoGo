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


@router.post("/zahlung", response_model=Zahlung, status_code=201)
def create_zahlung(
    zahlung: ZahlungCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_required)
):
    logger.info(f"Neue Zahlung wird erstellt für Vertrag ID: {zahlung.vertrag_id}")

    # Validate that amount is not negative
    if zahlung.betrag < 0:
        logger.warning("Ungültiger Betrag: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Der Betrag darf nicht negativ sein.")

    # Check if contract exists
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertrag_id).first()
    if not vertrag:
        logger.warning(f"Vertrag mit ID {zahlung.vertrag_id} wurde nicht gefunden.")
        raise HTTPException(status_code=404, detail="Vertrag wurde nicht gefunden.")

    # Validate payment date is not before contract start date
    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Ungültiges Zahlungsdatum: Darf nicht vor Vertragsbeginn liegen.")
        raise HTTPException(status_code=400, detail="Zahlungsdatum darf nicht vor Vertragsbeginn liegen.")

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
    logger.info(f"Zahlung erfolgreich erstellt mit ID: {db_zahlung.id}")
    return db_zahlung


@router.get("/zahlungen", response_model=List[Zahlung])
def list_zahlungen(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info("Alle Zahlungen werden abgerufen.")
    # Return empty list if no payments found
    zahlungen = db.query(ZahlungModel).all()
    return zahlungen


@router.put("/zahlungen/{zahlung_id}", response_model=Zahlung)
def update_zahlung(
    zahlung_id: int,
    zahlung_update: ZahlungUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_customer_required)
):
    logger.info(f"Zahlung mit ID {zahlung_id} wird aktualisiert.")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Zahlung mit ID {zahlung_id} wurde nicht gefunden.")
        raise HTTPException(status_code=404, detail=f"Zahlung mit ID {zahlung_id} wurde nicht gefunden.")

    # Only validate if amount is provided
    if zahlung_update.betrag is not None and zahlung_update.betrag < 0:
        logger.warning("Ungültiger Betrag bei Aktualisierung: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Der Betrag darf nicht negativ sein.")

    # Only check contract if vertrag_id is provided
    if zahlung_update.vertrag_id is not None:
        vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung_update.vertrag_id).first()
        if not vertrag:
            logger.warning(f"Vertrag mit ID {zahlung_update.vertrag_id} wurde nicht gefunden.")
            raise HTTPException(status_code=404, detail="Vertrag wurde nicht gefunden.")
        if zahlung_update.datum is not None and zahlung_update.datum < vertrag.beginnt_datum:
            logger.warning("Ungültiges Zahlungsdatum bei Aktualisierung: Darf nicht vor Vertragsbeginn liegen.")
            raise HTTPException(status_code=400, detail="Zahlungsdatum darf nicht vor Vertragsbeginn liegen.")

    # Apply updates only if values are provided
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
    logger.info(f"Zahlung mit ID {zahlung_id} wurde erfolgreich aktualisiert.")
    return zahlung


@router.delete("/zahlungen/{zahlung_id}", status_code=204)
def delete_zahlung(
    zahlung_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Versuch, Zahlung mit ID {zahlung_id} zu löschen.")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Zahlung mit ID {zahlung_id} wurde nicht gefunden.")
        raise HTTPException(status_code=404, detail="Zahlung wurde nicht gefunden.")

    # Delete payment record
    db.delete(zahlung)
    db.commit()
    logger.info(f"Zahlung mit ID {zahlung_id} wurde erfolgreich gelöscht.")
    return
