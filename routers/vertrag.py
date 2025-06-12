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

# Create a new contract (Vertrag)
@router.post("/vertrag", response_model=Vertrag, status_code=201)
def create_vertrag(vertrag: VertragCreate, db: Session = Depends(get_database_session), current_user: User = Depends(customer_required)):

    logger.info(f"Erstellung des Vertrags für Auto {vertrag.auto_id} und Kunde {vertrag.kunden_id}.")

    # Validate dates: start must be before end
    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Startdatum muss vor dem Enddatum liegen")
        raise HTTPException(status_code=400, detail="Startdatum muss vor dem Enddatum liegen.")

    # Validate minimum contract duration is 1 day
    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Vertragsdauer muss mindestens einen Tag betragen")
        raise HTTPException(status_code=400, detail="Vertragsdauer muss mindestens einen Tag betragen.")

    # Check if the car exists and is available
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Auto nicht gefunden")
        raise HTTPException(status_code=404, detail="Auto nicht gefunden.")
    if auto.status in ["beschädigt", "reserviert", "vermietet", "in_wartung", "außer_betrieb"]:
        logger.warning(f"Auto derzeit nicht verfügbar ({auto.status})")
        raise HTTPException(status_code=400, detail="Auto derzeit nicht verfügbar.")

    # Check if the customer exists
    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Kunde nicht gefunden")
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden.")

    # Mark car as rented (unavailable)
    auto.status = "reserviert"

    # Create new contract in database
    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    logger.info("Vertrag erfolgreich erstellt")

    # Commit new contract and update car status
    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    # Release car immediately if contract ended
    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = "verfügbar"
        db.commit()
        db.refresh(auto)
        logger.info(f"Auto {auto.id} sofort nach Vertragsende freigegeben.")

    return db_vertrag


# Cancel a contract before it starts
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(
    vertrag_id: int, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_or_customer_required)
):
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()

    if not vertrag:
        logger.warning("Vertrag nicht gefunden")
        raise HTTPException(status_code=404, detail="Der Vertrag wurde nicht gefunden.")

    # Cancellation not allowed after contract start date
    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Kündigung nach Vertragsbeginn nicht erlaubt")
        raise HTTPException(status_code=400, detail="Kündigung nach Vertragsbeginn ist nicht möglich.")

    # Mark contract as inactive
    vertrag.status = "beendet"                 

    # Free the car associated with the contract
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if auto:
        auto.status = "verfügbar"

    db.commit()
    if auto:
        db.refresh(auto)

    logger.info(f"Vertrag {vertrag_id} erfolgreich gekündigt.")

    return {"message": "Vertrag wurde erfolgreich gekündigt."}


# Update existing contract details
@router.put("/vertraege/{vertrag_id}", response_model=Vertrag)
def update_vertrag(vertrag_id: int, vertrag_update: VertragUpdate, db: Session = Depends(get_database_session), current_user: User = Depends(owner_required)):
    check_role(current_user, "owner")
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()

    if not vertrag:
        logger.warning("Vertrag nicht gefunden")
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden.")

    # Update car if new car id provided
    if vertrag_update.auto_id is not None:
        auto = db.query(Auto).filter(Auto.id == vertrag_update.auto_id).first()
        if not auto:
            logger.warning("Neues Auto nicht gefunden")
            raise HTTPException(status_code=404, detail="Neues Auto nicht gefunden.")
        vertrag.auto_id = vertrag_update.auto_id

    # Update customer if new customer id provided
    if vertrag_update.kunden_id is not None:
        kunde = db.query(Kunden).filter(Kunden.id == vertrag_update.kunden_id).first()
        if not kunde:
            logger.warning("Neuer Kunde nicht gefunden")
            raise HTTPException(status_code=404, detail="Neuer Kunde nicht gefunden.")
        vertrag.kunden_id = vertrag_update.kunden_id

    # Update dates, price, and status if provided
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

# Get all contracts (only accessible by owners)
@router.get("/vertraege", response_model=list[Vertrag])
def get_all_vertraege(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):

    logger.info(f"Benutzer mit Rolle 'owner' hat alle Verträge angefordert.")

    vertraege = db.query(vertrag_model).all()
    return vertraege


# Periodic update to free cars and deactivate contracts after end date
def zwischenstatus_aktualisieren(db: Session):
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
