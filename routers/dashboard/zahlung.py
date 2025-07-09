from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.zahlung import Zahlung as ZahlungModel
from models.vertrag import Vertrag as VertragModel  
from models.user import User
from schemas.zahlung import ZahlungCreate, Zahlung, ZahlungUpdate
from data_base import get_database_session
from core.logger_config import setup_logger
from services.dependencies import owner_required, owner_or_viewer_required, owner_or_editor_required
from pydantic import BaseModel

# Einfaches Antwortmodell mit einer Nachricht
class MessageResponse(BaseModel):
    message: str


logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/dashboard")

# =================== Hilfsfunktionen ===================

# Holt eine Zahlung anhand der ID oder wirft einen 404-Fehler
def get_zahlung(db: Session, zahlung_id: int) -> ZahlungModel:
    zahlung = db.query(ZahlungModel).filter(ZahlungModel.id == zahlung_id).first()
    if zahlung is None:
        logger.warning(f"Zahlung mit ID {zahlung_id} nicht gefunden.")
        raise HTTPException(status_code=404, detail=f"Zahlung mit ID {zahlung_id} nicht gefunden.")
    return zahlung

# Validiert eine neue Zahlung vor dem Anlegen
def validate_zahlung(db: Session, zahlung: ZahlungCreate):
    if zahlung.betrag < 0:
        logger.warning("Ungültiger Betrag: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Betrag darf nicht negativ sein.")
    
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertrag_id).first()
    if vertrag is None:
        logger.warning(f"Vertrag mit ID {zahlung.vertrag_id} nicht gefunden.")
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden.")
    
    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Ungültiges Zahlungsdatum: Zahlung darf nicht vor Vertragsbeginn liegen.")
        raise HTTPException(status_code=400, detail="Zahlungsdatum darf nicht vor Vertragsbeginn liegen.")

# Validiert eine Aktualisierung einer Zahlung
def validate_zahlung_update(db: Session, zahlung_update: ZahlungUpdate):
    if zahlung_update.betrag is not None and zahlung_update.betrag < 0:
        logger.warning("Ungültiger Betrag bei Update: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Betrag darf nicht negativ sein.")

    if zahlung_update.vertrag_id is not None:
        vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung_update.vertrag_id).first()
        if vertrag is None:
            logger.warning(f"Vertrag mit ID {zahlung_update.vertrag_id} nicht gefunden.")
            raise HTTPException(status_code=404, detail="Vertrag nicht gefunden.")

        if zahlung_update.datum is not None and zahlung_update.datum < vertrag.beginnt_datum:
            logger.warning("Ungültiges Zahlungsdatum bei Update: Zahlung darf nicht vor Vertragsbeginn liegen.")
            raise HTTPException(status_code=400, detail="Zahlungsdatum darf nicht vor Vertragsbeginn liegen.")

# Überträgt die Aktualisierungsdaten auf das bestehende Zahlungsobjekt
def apply_zahlung_update(zahlung: ZahlungModel, zahlung_update: ZahlungUpdate):
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

# =================== Zahlung anlegen ===================
@router.post(
    "/zahlungen", 
    response_model=Zahlung, 
    status_code=201,
    summary="Neue Zahlung für Vertrag erstellen"
)
def create_zahlung(
    zahlung: ZahlungCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Erstelle neue Zahlung für Vertrag ID: {zahlung.vertrag_id}")
    validate_zahlung(db, zahlung)

    db_zahlung = ZahlungModel(
        vertrag_id=zahlung.vertrag_id,
        zahlungsmethode=zahlung.zahlungsmethode,
        datum=zahlung.datum,
        status=zahlung.status,
        betrag=zahlung.betrag
    )
    try:
        db.add(db_zahlung)
        db.commit()
        db.refresh(db_zahlung)
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler beim Erstellen der Zahlung: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Speichern der Zahlung.")

    logger.info(f"Zahlung erfolgreich erstellt mit ID: {db_zahlung.id}")
    return db_zahlung

# =================== Alle Zahlungen abrufen ===================
@router.get(
    "/zahlungen", 
    response_model=List[Zahlung],
    summary="Alle Zahlungen abrufen"
)
def list_zahlungen(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_viewer_required)
):
    logger.info("Alle Zahlungen werden abgerufen.")
    zahlungen = db.query(ZahlungModel).all()
    return zahlungen

# =================== Zahlung aktualisieren ===================
@router.put(
    "/zahlungen/{zahlung_id}", 
    response_model=Zahlung,
    summary="Zahlung aktualisieren"
)
def update_zahlung(
    zahlung_id: int,
    zahlung_update: ZahlungUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_editor_required)
):
    logger.info(f"Zahlung mit ID {zahlung_id} wird aktualisiert.")
    zahlung = get_zahlung(db, zahlung_id)

    validate_zahlung_update(db, zahlung_update)
    apply_zahlung_update(zahlung, zahlung_update)

    db.commit()
    db.refresh(zahlung)
    logger.info(f"Zahlung mit ID {zahlung_id} erfolgreich aktualisiert.")
    return zahlung

# =================== Zahlung löschen ===================
@router.delete(
    "/zahlungen/{zahlung_id}",
    response_model=MessageResponse,
    status_code=200,
    summary="Zahlung löschen"
)
def delete_zahlung(
    zahlung_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Versuche Zahlung mit ID {zahlung_id} zu löschen.")
    zahlung = get_zahlung(db, zahlung_id)

    db.delete(zahlung)
    db.commit()
    logger.info(f"Zahlung mit ID {zahlung_id} erfolgreich gelöscht.")

    # Rückgabe einer Bestätigungsmeldung
    return {"message": f"Zahlung mit ID {zahlung_id} wurde erfolgreich gelöscht."}
