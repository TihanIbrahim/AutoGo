from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.zahlung import Zahlung as ZahlungModel
from models.vertrag import Vertrag as VertragModel  
from models.user import User
from schemas.zahlung import ZahlungCreate, Zahlung
from data_base import get_database_session
from core.logger_config import setup_logger
from services.dependencies import customer_or_guest_required

# Logger für dieses Modul initialisieren
logger = setup_logger(__name__)

# API-Router für zahlungsbezogene Endpunkte definieren
router = APIRouter(prefix="/api/v1")

# =================== Neue Zahlung erstellen ===================
@router.post(
    "/zahlungen",
    response_model=Zahlung,
    status_code=201,
    summary="Erstelle eine neue Zahlung für einen Vertrag"
)

def create_zahlung(
    zahlung: ZahlungCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_or_guest_required)
):
    # Versuch der Zahlungserstellung protokollieren
    logger.info(f"Erstelle neue Zahlung für Vertrag ID: {zahlung.vertrag_id}")

    # Prüfen, ob der Betrag negativ ist
    if zahlung.betrag < 0:
        logger.warning("Ungültiger Betrag: Betrag darf nicht negativ sein.")
        raise HTTPException(status_code=400, detail="Betrag darf nicht negativ sein.")

    # Prüfen, ob der zugehörige Vertrag existiert
    vertrag = db.query(VertragModel).filter(VertragModel.id == zahlung.vertrag_id).first()
    if vertrag is None:
        logger.warning(f"Vertrag mit ID {zahlung.vertrag_id} nicht gefunden.")
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden.")

    # Prüfen, ob das Zahlungsdatum vor dem Vertragsbeginn liegt
    if zahlung.datum < vertrag.beginnt_datum:
        logger.warning("Ungültiges Zahlungsdatum: Zahlung darf nicht vor Vertragsbeginn liegen.")
        raise HTTPException(status_code=400, detail="Zahlungsdatum darf nicht vor Vertragsbeginn liegen.")

    # Zahlung in der Datenbank anlegen
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

    # Erfolgreiche Zahlungserstellung protokollieren
    logger.info(f"Zahlung erfolgreich erstellt mit ID: {db_zahlung.id}")
    
    return db_zahlung
