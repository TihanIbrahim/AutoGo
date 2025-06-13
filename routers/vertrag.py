from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.vertrag import Vertrag as vertrag_model  
from models.auto import Auto  
from models.kunden import Kunden  
from models.user import User
from schemas.vertrag import VertragCreate, Vertrag, VertragUpdate  
from data_base import get_database_session
from logger_config import setup_logger
from services.dependencies import owner_or_customer_required, customer_required, owner_required
from services.auth_service import check_role

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

# =================== Vertrag helper function ===================
def get_vertrag(db: Session, vertrag_id: int) -> vertrag_model:
    """
    Retrieve a contract by ID or raise 404 if not found.
    """
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning(f"Vertrag mit ID {vertrag_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Vertrag mit ID {vertrag_id} nicht gefunden.")
    return vertrag

# =================== Create a new contract (Vertrag erstellen) ===================
@router.post("/vertrag", response_model=Vertrag, status_code=201)
def create_vertrag(vertrag: VertragCreate, db: Session = Depends(get_database_session), current_user: User = Depends(customer_required)):
    """
    Create a new contract if the car and customer exist and the contract dates are valid.
    """
    logger.info(f"Erstellung des Vertrags für Auto {vertrag.auto_id} und Kunde {vertrag.kunden_id}.")

    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Startdatum muss vor dem Enddatum liegen")
        raise HTTPException(status_code=400, detail="Startdatum muss vor dem Enddatum liegen.")

    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Vertragsdauer muss mindestens einen Tag betragen")
        raise HTTPException(status_code=400, detail="Vertragsdauer muss mindestens einen Tag betragen.")

    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Auto nicht gefunden")
        raise HTTPException(status_code=404, detail="Auto nicht gefunden.")
    if auto.status in ["beschädigt", "reserviert", "vermietet", "in_wartung", "außer_betrieb"]:
        logger.warning(f"Auto derzeit nicht verfügbar ({auto.status})")
        raise HTTPException(status_code=400, detail="Auto derzeit nicht verfügbar.")

    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Kunde nicht gefunden")
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden.")

    auto.status = "reserviert"

    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    logger.info("Vertrag erfolgreich erstellt")

    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = "verfügbar"
        db.commit()
        db.refresh(auto)
        logger.info(f"Auto {auto.id} sofort nach Vertragsende freigegeben.")

    return db_vertrag

# =================== Cancel a contract before it starts (Vertrag kündigen) ===================
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(
    vertrag_id: int, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_or_customer_required)
):
    """
    Cancel the contract if it has not started yet.
    """
    vertrag = get_vertrag(db, vertrag_id)

    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Kündigung nach Vertragsbeginn nicht erlaubt")
        raise HTTPException(status_code=400, detail="Kündigung nach Vertragsbeginn ist nicht möglich.")

    vertrag.status = "beendet"                 

    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if auto:
        auto.status = "verfügbar"

    db.commit()
    if auto:
        db.refresh(auto)

    logger.info(f"Vertrag {vertrag_id} erfolgreich gekündigt.")

    return {"message": "Vertrag wurde erfolgreich gekündigt."}

# =================== Update existing contract details (Vertrag aktualisieren) ===================
@router.put("/vertraege/{vertrag_id}", response_model=Vertrag)
def update_vertrag(vertrag_id: int, vertrag_update: VertragUpdate, db: Session = Depends(get_database_session), current_user: User = Depends(owner_required)):
    """
    Update contract details by owner with validation.
    """
    check_role(current_user, "owner")
    vertrag = get_vertrag(db, vertrag_id)

    if vertrag_update.auto_id is not None:
        auto = db.query(Auto).filter(Auto.id == vertrag_update.auto_id).first()
        if not auto:
            logger.warning("Neues Auto nicht gefunden")
            raise HTTPException(status_code=404, detail="Neues Auto nicht gefunden.")
        vertrag.auto_id = vertrag_update.auto_id

    if vertrag_update.kunden_id is not None:
        kunde = db.query(Kunden).filter(Kunden.id == vertrag_update.kunden_id).first()
        if not kunde:
            logger.warning("Neuer Kunde nicht gefunden")
            raise HTTPException(status_code=404, detail="Neuer Kunde nicht gefunden.")
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

    logger.info(f"Vertrag {vertrag_id} erfolgreich aktualisiert.")
    return vertrag

# =================== Get all contracts (Alle Verträge abrufen) ===================
@router.get("/vertraege", response_model=list[Vertrag])
def get_all_vertraege(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    """
    Retrieve all contracts; accessible by owners only.
    """
    logger.info(f"Benutzer mit Rolle 'owner' hat alle Verträge angefordert.")
    vertraege = db.query(vertrag_model).all()
    return vertraege

# =================== Periodic update to free cars and deactivate contracts (Periodische Aktualisierung) ===================
def zwischenstatus_aktualisieren(db: Session):
    """
    Periodically update contract statuses and free associated cars after contract ends.
    """
    alle_vertraege = db.query(vertrag_model).all()
    for vertrag in alle_vertraege:
        if vertrag.beendet_datum <= datetime.now().date():
            auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()

            if auto and auto.status != "verfügbar":
                auto.status = "verfügbar" 
                vertrag.status = "beendet"    
                db.commit()
                db.refresh(auto)
                db.refresh(vertrag)
                logger.info(f"Auto {auto.id} nach Vertragsende freigegeben, Vertrag {vertrag.id} deaktiviert.")
