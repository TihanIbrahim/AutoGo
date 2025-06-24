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

# Create a new contract
@router.post("/vertraege", response_model=Vertrag, status_code=201)
def create_vertrag(
    vertrag: VertragCreate, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_required)
):
    logger.info(f"User {current_user.id} creating contract for Auto {vertrag.auto_id} and Customer {vertrag.kunden_id}")

    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Start date must be before end date")
        raise HTTPException(status_code=400, detail="Start date must be before end date.")

    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Contract duration must be at least one day")
        raise HTTPException(status_code=400, detail="Contract duration must be at least one day.")

    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Car not found")
        raise HTTPException(status_code=404, detail="Car not found.")
    if auto.status in ["beschädigt", "reserviert", "vermietet", "in_wartung", "außer_betrieb"]:
        logger.warning(f"Car currently not available (status: {auto.status})")
        raise HTTPException(status_code=400, detail="Car currently not available.")

    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found.")

    auto.status = "reserviert"

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

    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = "verfügbar"
        db.commit()
        db.refresh(auto)
        logger.info(f"Car {auto.id} freed immediately after contract end")

    return db_vertrag

# Retrieve all contracts
@router.get("/vertraege", response_model=List[Vertrag])
def get_all_vertraege(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_viewer_required)
):
    logger.info("Dashboard: Retrieving all contracts")
    vertraege = db.query(vertrag_model).all()
    return vertraege

# Update contract
@router.put("/vertraege/{vertrag_id}", response_model=Vertrag)
def update_vertrag(
    vertrag_id: int, 
    vertrag_update: VertragUpdate, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_or_editor_required)
):
    logger.info(f"User {current_user.id} updating contract {vertrag_id}")

    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        raise HTTPException(status_code=404, detail=f"Contract with ID {vertrag_id} not found.")

    if vertrag_update.auto_id is not None:
        auto = db.query(Auto).filter(Auto.id == vertrag_update.auto_id).first()
        if not auto:
            logger.warning("New car not found")
            raise HTTPException(status_code=404, detail="New car not found.")
        vertrag.auto_id = vertrag_update.auto_id

    if vertrag_update.kunden_id is not None:
        kunde = db.query(Kunden).filter(Kunden.id == vertrag_update.kunden_id).first()
        if not kunde:
            logger.warning("New customer not found")
            raise HTTPException(status_code=404, detail="New customer not found.")
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
    logger.info(f"Contract {vertrag_id} updated successfully")
    return vertrag

# Cancel contract before it starts
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(
    vertrag_id: int, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(owner_required)
):
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        raise HTTPException(status_code=404, detail=f"Contract with ID {vertrag_id} not found.")

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
