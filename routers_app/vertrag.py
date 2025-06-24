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
from services.dependencies import customer_or_guest_required


logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

# =================== Vertrag helper function ===================
def get_vertrag(db: Session, vertrag_id: int) -> vertrag_model:
    # Fetch contract by ID or raise 404 if not found
    vertrag = db.query(vertrag_model).filter(vertrag_model.id == vertrag_id).first()
    if not vertrag:
        logger.warning(f"Contract with ID {vertrag_id} not found")
        raise HTTPException(status_code=404, detail=f"Contract with ID {vertrag_id} not found.")
    return vertrag

# =================== Create a new contract ===================
@router.post("/vertraege", response_model=Vertrag, status_code=201)
def create_vertrag(vertrag: VertragCreate, db: Session = Depends(get_database_session), current_user: User = Depends(customer_or_guest_required)):
    # Log contract creation attempt
    logger.info(f"Creating contract for car {vertrag.auto_id} and customer {vertrag.kunden_id}.")

    # Validate start date must be before end date
    if vertrag.beginnt_datum >= vertrag.beendet_datum:
        logger.warning("Start date must be before end date")
        raise HTTPException(status_code=400, detail="Start date must be before end date.")

    # Validate minimum contract duration of at least one day
    if (vertrag.beendet_datum - vertrag.beginnt_datum).days < 1:
        logger.warning("Contract duration must be at least one day")
        raise HTTPException(status_code=400, detail="Contract duration must be at least one day.")

    # Check if car exists
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        logger.warning("Car not found")
        raise HTTPException(status_code=404, detail="Car not found.")
    # Check if car is available for rental
    if auto.status in ["beschädigt", "reserviert", "vermietet", "in_wartung", "außer_betrieb"]:
        logger.warning(f"Car currently not available ({auto.status})")
        raise HTTPException(status_code=400, detail="Car currently not available.")

    # Check if customer exists
    kunde = db.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        logger.warning("Customer not found")
        raise HTTPException(status_code=404, detail="Customer not found.")

    # Set car status to reserved
    auto.status = "reserviert"

    # Create new contract object
    db_vertrag = vertrag_model(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=vertrag.beginnt_datum,
        beendet_datum=vertrag.beendet_datum,
        status=vertrag.status,
        total_preis=vertrag.total_preis
    )

    logger.info("Contract created successfully")

    # Add and commit new contract to the database
    db.add(db_vertrag)
    db.commit()
    db.refresh(db_vertrag)
    db.refresh(auto)

    # If contract end date already passed, free the car immediately
    if datetime.now().date() >= vertrag.beendet_datum:
        auto.status = "verfügbar"
        db.commit()
        db.refresh(auto)
        logger.info(f"Car {auto.id} freed immediately after contract end.")

    return db_vertrag

# =================== Cancel a contract before it starts ===================
@router.post("/vertraege/{vertrag_id}/kuendigen")
def vertrag_kuendigen(
    vertrag_id: int, 
    db: Session = Depends(get_database_session), 
    current_user: User = Depends(customer_or_guest_required)
):
    # Fetch contract by ID or raise 404
    vertrag = get_vertrag(db, vertrag_id)

    # Only allow cancellation if current date is before contract start date
    if datetime.now().date() >= vertrag.beginnt_datum:
        logger.warning("Cancellation not allowed after contract start date")
        raise HTTPException(status_code=400, detail="Cancellation after contract start is not allowed.")

    # Update contract status to ended
    vertrag.status = "beendet"                 

    # Find the associated car and mark it as available
    auto = db.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if auto:
        auto.status = "verfügbar"

    # Commit changes to the database
    db.commit()
    if auto:
        db.refresh(auto)

    logger.info(f"Contract {vertrag_id} cancelled successfully.")

    return {"message": "Contract was cancelled successfully."}

