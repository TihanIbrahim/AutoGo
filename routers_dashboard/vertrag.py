from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from data_base import get_database_session
from models.vertrag import Vertrag as vertrag_model  
from models.auto import Auto  
from models.kunden import Kunden  
from models.user import User
from schemas.vertrag import VertragCreate, Vertrag, VertragUpdate  
from logger_config import setup_logger
from services.dependencies import owner_required, owner_or_viewer_required, owner_or_editor_required

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/dashboard")

# =================== Vertrag erstellen ===================
@router.post("/vertraege", response_model=Vertrag, status_code=201)
def create_vertrag(
    vertrag: VertragCreate, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_required)  # Nur Besitzer dürfen Vertrag erstellen
):
    logger.info(f"User {current_user.id} erstellt Vertrag für Auto {vertrag.auto_id} und Kunde {vertrag.kunden_id}")

    # Prüfen ob das Startdatum vor dem Enddatum liegt
    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Startdatum muss vor Enddatum liegen")
        raise HTTPException(status_code=400, detail="Startdatum muss vor Enddatum liegen.")

    # Mindestdauer von 1 Tag sicherstellen
    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Vertragsdauer muss mindestens einen Tag sein")
        raise HTTPException(status_code=400, detail="Vertragsdauer muss mindestens einen Tag sein.")

    # Auto aus der DB holen und Verfügbarkeit prüfen
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Auto nicht gefunden")
        raise HTTPException(status_code=404, detail="Auto nicht gefunden.")
    if auto.status in ["beschädigt", "reserviert", "vermietet", "in_wartung", "außer_betrieb"]:
        logger.warning(f"Auto derzeit nicht verfügbar (Status: {auto.status})")
        raise HTTPException(status_code=400, detail="Auto derzeit nicht verfügbar.")

    # Kunde aus der DB holen und Existenz prüfen
    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Kunde nicht gefunden")
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden.")

    # Auto Status auf reserviert setzen
    auto.status = "reserviert"

    # Neuen Vertrag erstellen
    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    # Falls der Vertrag sofort abgelaufen ist, Auto direkt freigeben
    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = "verfügbar"
        db.commit()
        db.refresh(auto)
        logger.info(f"Auto {auto.id} sofort nach Vertragsende freigegeben")

    return db_vertrag

# =================== Alle Verträge abrufen ===================
@router.get("/vertraege", response_model=List[Vertrag])
def get_all_vertraege(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_viewer_required)  # Besitzer und Viewer dürfen alle Verträge sehen
):
    logger.info("Alle Verträge werden abgerufen")
    vertraege = db.query(vertrag_model).all()
    return vertraege

# =================== Vertrag aktualisieren ===================
@router.put("/vertraege/{vertrag_id}", response_model=Vertrag)
def update_vertrag(
    vertrag_id: int, 
    vertrag_update: VertragUpdate, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_or_editor_required)  # Besitzer und Editor dürfen Vertrag ändern
):
    logger.info(f"Vertrag {vertrag_id} wird aktualisiert")

    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning(f"Vertrag mit ID {vertrag_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Vertrag mit ID {vertrag_id} nicht gefunden.")

    # Auto wechseln, falls angegeben und Auto existiert
    if vertrag_update.auto_id is not None:
        auto = db.query(Auto).filter(Auto.id == vertrag_update.auto_id).first()
        if not auto:
            logger.warning("Neues Auto nicht gefunden")
            raise HTTPException(status_code=404, detail="Neues Auto nicht gefunden.")
        vertrag.auto_id = vertrag_update.auto_id

    # Kunde wechseln, falls angegeben und Kunde existiert
    if vertrag_update.kunden_id is not None:
        kunde = db.query(Kunden).filter(Kunden.id == vertrag_update.kunden_id).first()
        if not kunde:
            logger.warning("Neuer Kunde nicht gefunden")
            raise HTTPException(status_code=404, detail="Neuer Kunde nicht gefunden.")
        vertrag.kunden_id = vertrag_update.kunden_id

    # Weitere Felder aktualisieren falls angegeben
    if vertrag_update.beginnt_datum is not None:
        vertrag.beginnt_datum = vertrag_update.beginnt_datum
    if vertrag_update.beendet_datum is not None:
        vertrag.beendet_datum = vertrag_update.beendet_datum
    if vertrag_update.total_preis is not None:
        vertrag.total_preis = vertrag_update.total_preis
    if vertrag_update.status is not None:
        vertrag.status = vertrag_update.status

    db.commit()
    db.refresh(vertrag)
    logger.info(f"Vertrag {vertrag_id} erfolgreich aktualisiert")
    return vertrag

# =================== Vertrag vor Vertragsbeginn kündigen ===================
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(
    vertrag_id: int, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_required)  # Nur Besitzer dürfen Vertrag kündigen
):
    logger.info(f"Versuche Vertrag {vertrag_id} zu kündigen")

    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning(f"Vertrag mit ID {vertrag_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Vertrag mit ID {vertrag_id} nicht gefunden.")

    # Kündigung nur möglich, wenn Vertrag noch nicht begonnen hat
    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Kündigung nach Vertragsbeginn nicht erlaubt")
        raise HTTPException(status_code=400, detail="Kündigung nach Vertragsbeginn ist nicht möglich.")

    # Vertrag auf beendet setzen und Auto freigeben
    vertrag.status = "beendet"
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if auto:
        auto.status = "verfügbar"

    db.commit()
    if auto:
        db.refresh(auto)

    logger.info(f"Vertrag {vertrag_id} erfolgreich gekündigt")
    return {"message": "Vertrag wurde erfolgreich gekündigt."}
