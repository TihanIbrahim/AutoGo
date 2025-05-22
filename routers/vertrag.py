from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.vertrag import Vertrag as vertrag_model  
from models.auto import Auto  
from models.kunden import Kunden  
from schemas.vertrag import VertragCreate, Vertrag, VertragUpdate  
from data_base import get_database_session
from logger_config import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

@router.post("/vertrag", response_model=Vertrag,status_code=201)
def create_vertrag(vertrag: VertragCreate, db: Session = Depends(get_database_session)):
    logger.info(f"Vertrag für Auto {vertrag.auto_id} und Kunde {vertrag.kunden_id} wird erstellt.")

    # Check that start date is before end date
    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Beginndatum muss vor Enddatum liegen")
        raise HTTPException(status_code=400, detail="Beginndatum muss vor dem Enddatum liegen.")

    # Check car exists
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Auto wurde nicht gefunden")
        raise HTTPException(status_code=404, detail="Auto wurde nicht gefunden.")
    # Check car is available
    if auto.status is False:
        logger.warning("Auto ist derzeit nicht verfügbar")
        raise HTTPException(status_code=400, detail="Auto ist derzeit nicht verfügbar.")

    # Check customer exists
    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Kunde wurde nicht gefunden")
        raise HTTPException(status_code=404, detail="Kunde wurde nicht gefunden.")

    # Mark car as rented (not available)
    auto.status = False

    # Create contract record
    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    logger.info("Vertrag erfolgreich erstellt")

    # Save contract and car status
    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    # If contract already ended, free the car
    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = True
        db.commit()
        db.refresh(auto)
        logger.info(f"Auto {auto.id} wurde sofort nach Vertragsende freigegeben.")

    return db_vertrag

@router.post("/Verträge/{vertrag_id}/kuendigen", response_model=dict)
def vertrag_kuendigen(vertrag_id: int, db: Session = Depends(get_database_session)):
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning("Vertrag wurde nicht gefunden")
        raise HTTPException(status_code=404, detail="Vertrag wurde nicht gefunden.")

    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Kündigung nach Vertragsbeginn ist nicht möglich.")
        raise HTTPException(status_code=400, detail="Kündigung nach Vertragsbeginn ist nicht möglich.")
    
    vertrag.status = False

    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if auto:
        auto.status = True

    db.commit()
    if auto:
        db.refresh(auto)

    logger.info(f"Vertrag {vertrag_id} wurde erfolgreich gekündigt.")
    return {"message": "Vertrag wurde erfolgreich gekündigt."}

@router.put("/Verträge/{vertrag_id}", response_model=Vertrag)
def update_vertrag(vertrag_id: int, vertrag_update: VertragUpdate, db: Session = Depends(get_database_session)):
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning("Vertrag wurde nicht gefunden.")
        raise HTTPException(status_code=404, detail="Vertrag wurde nicht gefunden.")

    if vertrag_update.auto_id is not None:
        auto = db.query(Auto).filter(Auto.id == vertrag_update.auto_id).first()
        if not auto:
            logger.warning("Neues Auto wurde nicht gefunden.")
            raise HTTPException(status_code=404, detail="Neues Auto wurde nicht gefunden.")
        vertrag.auto_id = vertrag_update.auto_id

    if vertrag_update.kunden_id is not None:
        kunde = db.query(Kunden).filter(Kunden.id == vertrag_update.kunden_id).first()
        if not kunde:
            logger.warning("Neuer Kunde wurde nicht gefunden.")
            raise HTTPException(status_code=404, detail="Neuer Kunde wurde nicht gefunden.")
        vertrag.kunden_id = vertrag_update.kunden_id

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

    logger.info(f"Vertrag {vertrag_id} wurde erfolgreich aktualisiert.")
    return vertrag

def zwischenstatus_aktualisieren(db: Session):
    alle_vertraege = db.query(vertrag_model).all()
    for vertrag in alle_vertraege:
        if vertrag.beendet_datum <= datetime.now().date():
            auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
            if auto and auto.status is False:
                auto.status = True
                vertrag.status = False
                db.commit()
                db.refresh(auto)
                db.refresh(vertrag)
                logger.info(f"Auto {auto.id} wurde nach Vertragsende freigegeben, Vertrag {vertrag.id} deaktiviert.")
