from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from data_base import get_database_session
from models.kunden import Kunden as kundenmodel
from schemas.kunden import KundenCreate, Kunden, KundenUpdate
from logger_config import setup_logger
from typing import List

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

@router.post("/kunde", response_model=Kunden, status_code=201)
def create_kunden(kunden: KundenCreate, db_session: Session = Depends(get_database_session)):
    logger.info(f"Erstelle Kunde: {kunden.vorname} {kunden.nachname}")
    db_kunden = kundenmodel(
        vorname=kunden.vorname,
        nachname=kunden.nachname,
        geb_datum=kunden.geb_datum,
        handy_nummer=kunden.handy_nummer,
        email=kunden.email
    )
    db_session.add(db_kunden)
    db_session.commit()
    db_session.refresh(db_kunden)
    logger.info(f"Kunde erfolgreich erstellt mit ID: {db_kunden.id}")
    return db_kunden  # Return the created customer


@router.get("/kunden", response_model=List[Kunden])
def list_kunden(db: Session = Depends(get_database_session)):
    logger.info("Alle Kunden abrufen")
    kunden = db.query(kundenmodel).all()
    if not kunden:
        logger.warning("Keine Kunden gefunden")
        raise HTTPException(status_code=404, detail="Keine Kunden vorhanden.")
    return kunden



@router.delete("/kunden/{kunden_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kunde(kunden_id: int, db: Session = Depends(get_database_session)):
    logger.info(f"Versuche Kunde zu löschen mit ID: {kunden_id}")
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit der ID {kunden_id} wurde nicht gefunden.")

    db.delete(kunde)
    db.commit()
    logger.info(f"Kunde mit ID {kunden_id} wurde gelöscht")
    return None  # No content returned (204)


@router.get("/kunden/{kunden_id}", response_model=Kunden)
def get_kunde(kunden_id: int, db: Session = Depends(get_database_session)):
    logger.info(f"Kunde abrufen mit ID: {kunden_id}")
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit der ID {kunden_id} wurde nicht gefunden.")

    return kunde  # Return the customer details


@router.put("/kunden/{kunden_id}", response_model=Kunden)
def update_kunde(kunden_id: int, kunde_update: KundenUpdate, db: Session = Depends(get_database_session)):
    logger.info(f"Kunde aktualisieren mit ID: {kunden_id}")
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit der ID {kunden_id} wurde nicht gefunden.")

    # Update customer fields if provided
    if kunde_update.vorname is not None:
        kunde.vorname = kunde_update.vorname
    if kunde_update.nachname is not None:
        kunde.nachname = kunde_update.nachname
    if kunde_update.geb_datum is not None:
        kunde.geb_datum = kunde_update.geb_datum
    if kunde_update.handy_nummer is not None:
        kunde.handy_nummer = kunde_update.handy_nummer
    if kunde_update.email is not None:
        kunde.email = kunde_update.email

    db.commit()
    db.refresh(kunde)
    logger.info(f"Kunde mit ID {kunden_id} erfolgreich aktualisiert")
    return kunde  # Return the updated customer
