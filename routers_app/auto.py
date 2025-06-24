from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from models.auto import Auto as AutoModel, AutoStatus
from schemas.auto import  Auto
from data_base import get_database_session
from logger_config import setup_logger
from datetime import datetime
from services.dependencies import customer_or_guest_required
from models.user import User

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1")

# Helper function to fetch a car by ID or raise 404 error
def get_auto_by_id(db: Session, auto_id: int) -> AutoModel:
    auto = db.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto:
        logger.warning(f"Auto mit ID {auto_id} nicht gefunden")  # Car not found
        raise HTTPException(status_code=404, detail=f"Auto mit ID {auto_id} nicht gefunden.")
    return auto

# Helper function to validate that the hourly price is greater than 0
def validate_preis_pre_stunde(preis: float):
    if preis <= 0:
        logger.warning("Ungültiger Stundenpreis (<= 0)")  # Invalid hourly price
        raise HTTPException(status_code=400, detail="Der Stundenpreis muss größer als 0 sein.")


# =================== Autos suchen ===================
# Endpoint to search cars with optional filters
@router.get("/autos/search", response_model=List[Auto])
def search_auto(
    brand: Optional[str] = Query(None, description="Marke des Autos"),
    model: Optional[str] = Query(None, description="Modell des Autos"),
    jahr: Optional[int] = Query(None, ge=2000, le=datetime.now().year, description="Baujahr"),
    status: Optional[AutoStatus] = Query(None, description="Status des Autos"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_or_guest_required)
):
    logger.info(f"Autosuche: Marke={brand}, Modell={model}, Jahr={jahr}, Status={status}")

    query = db.query(AutoModel)

    if brand:
        query = query.filter(AutoModel.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(AutoModel.model.ilike(f"%{model}%"))
    if jahr:
        query = query.filter(AutoModel.jahr == jahr)
    if status:
        query = query.filter(AutoModel.status == status)

    result = query.all()

    logger.info(f"{len(result)} Autos gefunden.")  # Zeige wie viele Autos gefunden wurden
    return result  



# =================== Gesamtpreis berechnen ===================
# Endpoint to calculate total rental price
@router.post("/autos/{auto_id}/calculate-price")
def calculate_total_price(
    auto_id: int = Path(..., gt=0, description="Die ID des Autos (muss > 0 sein)"),
    mietdauer_stunden: int = Query(..., gt=0, description="Mietdauer in Stunden (muss > 0 sein)"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(customer_or_guest_required)
):
    logger.info(f"Gesamtpreisberechnung für Auto ID {auto_id} mit Mietdauer {mietdauer_stunden} Stunden")  # Price calculation started
    auto = get_auto_by_id(db, auto_id)

    if auto.status != AutoStatus.verfügbar:
        logger.warning("Auto derzeit nicht verfügbar")  # Car not available
        raise HTTPException(status_code=400, detail="Das Auto ist momentan nicht verfügbar.")

    total_price = auto.preis_pro_stunde * mietdauer_stunden
    logger.info(f"Gesamtpreis berechnet: {total_price} EUR")  # Total price calculated
    return {
        "auto_id": auto_id,
        "rental_duration_hours": mietdauer_stunden,
        "price_per_hour": auto.preis_pro_stunde,
        "total_price": total_price
    }