from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from models.auto import Auto as AutoModel, AutoStatus
from schemas.auto import AutoCreate, Auto, AutoUpdate
from data_base import get_database_session
from logger_config import setup_logger
from datetime import datetime
from services.dependencies import owner_required, owner_or_customer_required
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

# =================== Auto erstellen ===================
# Endpoint to create a new car
@router.post("/auto", response_model=Auto, status_code=201)
def create_auto(
    auto: AutoCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Auto wird erstellt: {auto.brand} {auto.model}")  # Creating a car
    validate_preis_pre_stunde(auto.preis_pro_stunde)

    db_auto = AutoModel(
        brand=auto.brand,
        model=auto.model,
        jahr=auto.jahr,
        preis_pro_stunde=auto.preis_pro_stunde,
        status=auto.status,
    )
    db.add(db_auto)
    db.commit()
    db.refresh(db_auto)
    logger.info(f"Auto erfolgreich erstellt mit ID: {db_auto.id}")  # Car successfully created
    return db_auto

# =================== Alle verfügbaren Autos anzeigen ===================
# Endpoint to get all available cars
@router.get("/autos", response_model=List[Auto])
def show_all_auto(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info("Alle verfügbaren Autos werden abgerufen")  # Fetching all available cars
    autos = db.query(AutoModel).filter(AutoModel.status == AutoStatus.verfügbar).all()
    if not autos:
        logger.info("Keine verfügbaren Autos gefunden")  # No cars available
    return autos

# =================== Autos suchen ===================
# Endpoint to search cars with optional filters
@router.get("/autos/search", response_model=List[Auto])
def search_auto(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    jahr: Optional[int] = Query(None, ge=2000, le=datetime.now().year),
    status: Optional[AutoStatus] = None,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_customer_required)
):
    logger.info(f"Autosuche: Marke={brand}, Modell={model}, Jahr={jahr}, Status={status}")  # Car search log
    query = db.query(AutoModel)
    if brand:
        query = query.filter(AutoModel.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(AutoModel.model.ilike(f"%{model}%"))
    if jahr:
        query = query.filter(AutoModel.jahr == jahr)
    if status is not None:
        query = query.filter(AutoModel.status == status)
    result = query.all()
    if not result:
        logger.warning("Keine passenden Autos gefunden")  # No matching cars found
        raise HTTPException(status_code=404, detail="Keine passenden Autos gefunden.")
    return result

# =================== Auto aktualisieren ===================
# Endpoint to update a car
@router.put("/autos/{auto_id}", response_model=Auto)
def update_auto(
    auto_id: int,
    auto_update: AutoUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Auto mit ID {auto_id} wird aktualisiert")  # Updating car
    auto = get_auto_by_id(db, auto_id)

    if auto_update.preis_pro_stunde is not None:
        validate_preis_pre_stunde(auto_update.preis_pro_stunde)
        auto.preis_pro_stunde = auto_update.preis_pro_stunde
    if auto_update.brand is not None:
        auto.brand = auto_update.brand
    if auto_update.model is not None:
        auto.model = auto_update.model
    if auto_update.jahr is not None:
        auto.jahr = auto_update.jahr
    if auto_update.status is not None:
        auto.status = auto_update.status

    db.commit()
    db.refresh(auto)
    logger.info(f"Auto mit ID {auto_id} wurde erfolgreich aktualisiert")  # Car updated
    return auto

# =================== Auto löschen ===================
# Endpoint to delete a car
@router.delete("/autos/{auto_id}", status_code=204)
def delete_auto(
    auto_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Löschvorgang für Auto mit ID {auto_id} wird gestartet")  # Deletion started
    auto = get_auto_by_id(db, auto_id)

    db.delete(auto)
    db.commit()
    logger.info(f"Auto mit ID {auto_id} wurde erfolgreich gelöscht")  # Car deleted
    return

# =================== Auto anzeigen ===================
# Endpoint to get details of a specific car
@router.get("/autos/{auto_id}", response_model=Auto)
def show_auto(
    auto_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Auto mit ID {auto_id} wird angezeigt")  # Showing car
    auto_details = get_auto_by_id(db, auto_id)
    return auto_details

# =================== Gesamtpreis berechnen ===================
# Endpoint to calculate total rental price
@router.post("/autos/{auto_id}/calculate-price")
def calculate_total_price(
    auto_id: int = Path(..., gt=0, description="Die ID des Autos (muss > 0 sein)"),
    mietdauer_stunden: int = Query(..., gt=0, description="Mietdauer in Stunden (muss > 0 sein)"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_customer_required)
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
