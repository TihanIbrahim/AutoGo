from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from models.zahlung import Zahlung as ZahlungModel
from models.vertrag import Vertrag as VertragModel  
from schemas.zahlung import ZahlungCreate, Zahlung, ZahlungUpdate
from data_base import get_database_session
from logger_config import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Zahlungen"])


@router.post("/zahlung", response_model=Zahlung, status_code=201)
def create_zahlung(zahlung: ZahlungCreate, db: Session = Depends(get_database_session)):
    logger.info(f"Neue Zahlung wird erstellt für Vertrag ID: {zahlung.vertragid}")

    # validate negative amount
    if zahlung.betrag < 0:
        logger.warning("Ungültiger Betrag: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Der Betrag darf nicht negativ sein.")

    # validate contract existence and payment date
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertragid).first()
    if not vertrag:
        logger.warning(f"Vertrag mit ID {zahlung.vertragid} nicht gefunden.")
        raise HTTPException(status_code=404, detail="Vertrag wurde nicht gefunden.")

    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Ungültiges Zahlungsdatum: vor Vertragsbeginn.")
        raise HTTPException(status_code=400, detail="Das Zahlungsdatum darf nicht vor dem Vertragsbeginn liegen.")

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
    logger.info(f"Zahlung erfolgreich erstellt mit ID: {db_zahlung.id}")
    return db_zahlung


@router.get("/zahlungen", response_model=List[Zahlung])
def list_zahlungen(db: Session = Depends(get_database_session)):
    logger.info("Abruf aller Zahlungen")
    zahlungen = db.query(ZahlungModel).all()
    if not zahlungen:
        logger.warning("Keine Zahlungen gefunden")
        raise HTTPException(status_code=404, detail="Keine Zahlungen gefunden.")
    return zahlungen


@router.get("/zahlungen/{zahlung_id}", response_model=Zahlung)
def get_zahlung(zahlung_id: int, db: Session = Depends(get_database_session)):
    logger.info(f"Abruf der Zahlung mit ID: {zahlung_id}")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Zahlung mit ID {zahlung_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Zahlung mit der ID {zahlung_id} wurde nicht gefunden.")
    return zahlung


@router.put("/zahlungen/{zahlung_id}", response_model=Zahlung)
def update_zahlung(zahlung_id: int, zahlung_update: ZahlungUpdate, db: Session = Depends(get_database_session)):
    logger.info(f"Zahlung mit ID {zahlung_id} wird aktualisiert")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Zahlung mit ID {zahlung_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Zahlung mit der ID {zahlung_id} wurde nicht gefunden.")

    # validate negative amount
    if zahlung_update.betrag < 0:
        logger.warning("Ungültiger Betrag bei Update: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Der Betrag darf nicht negativ sein.")

    # validate contract and payment date
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung_update.vertragid).first()
    if not vertrag:
        logger.warning(f"Vertrag mit ID {zahlung_update.vertragid} nicht gefunden.")
        raise HTTPException(status_code=404, detail="Vertrag wurde nicht gefunden.")

    if zahlung_update.datum < vertrag.beginnt_datum:
        logger.warning("Ungültiges Zahlungsdatum beim Update: vor Vertragsbeginn.")
        raise HTTPException(status_code=400, detail="Das Zahlungsdatum darf nicht vor dem Vertragsbeginn liegen.")

    zahlung.vertragid = zahlung_update.vertragid
    zahlung.zahlungsmethode = zahlung_update.zahlungsmethode
    zahlung.datum = zahlung_update.datum
    zahlung.status = zahlung_update.status
    zahlung.betrag = zahlung_update.betrag

    db.commit()
    db.refresh(zahlung)
    logger.info(f"Zahlung mit ID {zahlung_id} erfolgreich aktualisiert")
    return zahlung


@router.delete("/zahlungen/{zahlung_id}", status_code=204)
def delete_zahlung(zahlung_id: int, db: Session = Depends(get_database_session)):
    logger.info(f"Versuche, Zahlung mit ID {zahlung_id} zu löschen")
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if not zahlung:
        logger.warning(f"Zahlung mit ID {zahlung_id} nicht gefunden")
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")

    db.delete(zahlung)
    db.commit()
    logger.info(f"Zahlung mit ID {zahlung_id} erfolgreich gelöscht")
