from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.vertrag import Vertrag as vertrag_model  
from models.auto import Auto, AutoStatus  
from models.user import User
from schemas.vertrag import VertragCreate, Vertrag  
from data_base import get_database_session
from logger_config import setup_logger
from services.dependencies import customer_or_guest_required
from routers_app.auto import get_available_auto  
from routers_app.kunden import get_kunde  

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

# =================== Vertrag abrufen ===================
def get_vertrag(db: Session, vertrag_id: int) -> vertrag_model:
    # Vertrag anhand der ID abrufen, 404 Fehler wenn nicht gefunden
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning(f"Contract mit ID {vertrag_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Contract mit ID {vertrag_id} nicht gefunden.")
    return vertrag

# =================== Vertrag erstellen ===================
@router.post("/vertraege", response_model=Vertrag, status_code=201)
def create_vertrag(
    vertrag: VertragCreate, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(customer_or_guest_required)
):
    # Erstellung des Vertrags protokollieren
    logger.info(f"Erstelle Vertrag für Auto {vertrag.auto_id} und Kunde {vertrag.kunden_id}.")

    # Validierung: Startdatum muss vor Enddatum liegen
    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Startdatum muss vor Enddatum liegen")
        raise HTTPException(status_code=400, detail="Startdatum muss vor Enddatum liegen.")

    # Validierung: Vertragsdauer muss mindestens einen Tag betragen
    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Vertragsdauer muss mindestens einen Tag betragen")
        raise HTTPException(status_code=400, detail="Vertragsdauer muss mindestens einen Tag betragen.")

    # Auto und Kunde abrufen und prüfen
    auto = get_available_auto(db, vertrag.auto_id)
    kunde = get_kunde(db, vertrag.kunden_id)

    # Auto als reserviert markieren
    auto.status = AutoStatus.reserviert

    # Vertrag anlegen
    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    # Vertrag speichern und Auto aktualisieren
    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    # Auto sofort freigeben, falls Vertragsende bereits erreicht oder überschritten ist
    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = AutoStatus.verfügbar
        db.commit()
        db.refresh(auto)
        logger.info(f"Auto {auto.id} nach Vertragsende sofort freigegeben.")

    logger.info(f"Vertrag {db_vertrag.id} erfolgreich erstellt.")
    return db_vertrag

# =================== Vertrag kündigen ===================
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(
    vertrag_id: int, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(customer_or_guest_required)
):
    # Vertrag abrufen
    vertrag = get_vertrag(db, vertrag_id)

    # Kündigung vor Vertragsbeginn prüfen
    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Kündigung nach Vertragsbeginn nicht erlaubt")
        raise HTTPException(status_code=400, detail="Kündigung nach Vertragsbeginn ist nicht erlaubt.")

    # Auto zum Vertrag abrufen
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning(f"Auto mit ID {vertrag.auto_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Auto mit ID {vertrag.auto_id} nicht gefunden.")

    # Vertrag und Auto Status aktualisieren
    vertrag.status = "beendet"
    auto.status = AutoStatus.verfügbar

    # Änderungen speichern
    db.commit()

    logger.info(f"Vertrag {vertrag_id} erfolgreich gekündigt.")
    return {"message": "Vertrag wurde erfolgreich gekündigt."}
