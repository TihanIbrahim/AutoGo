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
from services.dependencies import owner_or_customer_required ,customer_required ,owner_required
from services.auth_service import check_role

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

# Create a new contract (Vertrag)
@router.post("/vertrag", response_model=Vertrag, status_code=201)
def create_vertrag(vertrag: VertragCreate, db: Session = Depends(get_database_session), current_user: User = Depends(customer_required)):

    logger.info(f"Creating contract for Auto {vertrag.auto_id} and Customer {vertrag.kunden_id}.")

    # Validate dates: start must be before end
    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Start date must be before end date")
        raise HTTPException(status_code=400, detail="Start date must be before end date.")

    # Validate minimum contract duration is 1 day
    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Contract duration must be at least one day")
        raise HTTPException(status_code=400, detail="Contract duration must be at least one day.")

    # Check if the car exists and is available
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Car not found")
        raise HTTPException(status_code=404, detail="Car not found.")
    if auto.status is False:
        logger.warning("Car is currently not available")
        raise HTTPException(status_code=400, detail="Car is currently not available.")

    # Check if the customer exists
    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found.")

    # Mark car as rented (unavailable)
    auto.status = False

    # Create new contract in database
    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    logger.info("Contract created successfully")

    # Commit new contract and update car status
    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    # Release car immediately if contract ended
    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = True
        db.commit()
        db.refresh(auto)
        logger.info(f"Car {auto.id} released immediately after contract end.")

    return db_vertrag


# Cancel a contract before it starts
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(vertrag_id: int, db: Session = Depends(get_database_session), current_user: User = Depends(owner_or_customer_required)):
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()

    if not vertrag:
        logger.warning("Contract not found")
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Cancellation not allowed after contract start date
    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Cancellation after contract start date not allowed")
        raise HTTPException(status_code=400, detail="Kündigung nach Vertragsbeginn ist nicht möglich.")

    # Mark contract as inactive
    vertrag.status = False

    # Free the car associated with the contract
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if auto:
        auto.status = True

    db.commit()
    if auto:
        db.refresh(auto)

    logger.info(f"Contract {vertrag_id} cancelled successfully.")

    return {"message": "Vertrag wurde erfolgreich gekündigt."}



# Update existing contract details
@router.put("/vertraege/{vertrag_id}", response_model=Vertrag)
def update_vertrag(vertrag_id: int, vertrag_update: VertragUpdate, db: Session = Depends(get_database_session), current_user: User = Depends(owner_required)):
    check_role(current_user, "owner")
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()

    if not vertrag:
        logger.warning("Contract not found")
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Update car if new car id provided
    if vertrag_update.auto_id is not None:
        auto = db.query(Auto).filter(Auto.id == vertrag_update.auto_id).first()
        if not auto:
            logger.warning("New car not found")
            raise HTTPException(status_code=404, detail="New car not found.")
        vertrag.auto_id = vertrag_update.auto_id

    # Update customer if new customer id provided
    if vertrag_update.kunden_id is not None:
        kunde = db.query(Kunden).filter(Kunden.id == vertrag_update.kunden_id).first()
        if not kunde:
            logger.warning("New customer not found")
            raise HTTPException(status_code=404, detail="New customer not found.")
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

    logger.info(f"Contract {vertrag_id} updated successfully.")
    return vertrag

# Get all contracts (only accessible by owners)
@router.get("/vertraege", response_model=list[Vertrag])
def get_all_vertraege(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):

    logger.info(f"User with role 'owner' requested all contracts.")

    vertraege = db.query(vertrag_model).all()
    return vertraege



# Periodic update to free cars and deactivate contracts after end date
def zwischenstatus_aktualisieren(db: Session):
    alle_vertraege = db.query(vertrag_model).all()
    for vertrag in alle_vertraege:
        if vertrag.beendet_datum <= datetime.now().date():
            auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
            if auto and auto.status is False:
                auto.status = True  # Free the car
                vertrag.status = False  # Deactivate contract
                db.commit()
                db.refresh(auto)
                db.refresh(vertrag)
                logger.info(f"Car {auto.id} released after contract end, contract {vertrag.id} deactivated.")  