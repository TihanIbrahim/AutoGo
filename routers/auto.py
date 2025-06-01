from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.auto import Auto as AutoModel
from schemas.auto import AutoCreate, Auto, AutoUpdate
from data_base import get_database_session
from logger_config import setup_logger
from datetime import datetime
from services.auth_service import check_role
from services.dependencies import get_current_user
from models.user import User

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

@router.post("/auto", response_model=Auto, status_code=201)
def create_auto(auto: AutoCreate, db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    # Check if user has 'owner' role before creating auto
    check_role(current_user, "owner")
    logger.info(f"Creating auto: {auto.brand} {auto.model}")

    # Validate price per hour must be positive
    if auto.preis_pro_stunde <= 0:
        logger.warning("Invalid price per hour (<= 0)")
        raise HTTPException(status_code=400, detail="Price per hour must be greater than 0.")

    # Create new Auto record
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
    logger.info(f"Auto created successfully with ID: {db_auto.id}")
    return db_auto


@router.get("/autos", response_model=List[Auto])
def show_all_auto(db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    # Check if user is 'owner' before listing autos
    check_role(current_user, "owner")
    logger.info("Request: Fetch all available autos")

    # Query all autos with status = True (available)
    autos = db.query(AutoModel).filter(AutoModel.status.is_(True)).all()

    if not autos:
        logger.warning("No available autos found")
        raise HTTPException(status_code=404, detail="No available autos found at the moment.")
    return autos


@router.get("/autos/search", response_model=List[Auto])
def search_auto(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    jahr: Optional[int] = Query(None, ge=2000, le=datetime.now().year),
    status: Optional[bool] = None,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    # Allow 'owner' to search autos
    check_role(current_user, ["owner", "customer"])

    logger.info(f"Searching autos: brand={brand}, model={model}, jahr={jahr}, status={status}")

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
        logger.warning("No matching autos found")
        raise HTTPException(status_code=404, detail="No matching autos found.")
    return result


@router.get("/autos/{auto_id}", response_model=Auto)
def show_auto(auto_id: int, db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    # Only 'owner' can get auto by ID
    check_role(current_user, "owner")
    logger.info(f"Fetching auto with ID: {auto_id}")

    auto_details = db.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto_details:
        logger.warning(f"Auto with ID {auto_id} not found")
        raise HTTPException(status_code=404, detail=f"Auto with ID {auto_id} not found.")
    return auto_details


@router.put("/autos/{auto_id}", response_model=Auto)
def update_auto(auto_id: int, auto_update: AutoUpdate, db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
 # Only 'owner' can update autos
    check_role(current_user, "owner")

    logger.info(f"Updating auto with ID: {auto_id}")

    auto = db.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto:
        logger.warning(f"Auto with ID {auto_id} does not exist")
        raise HTTPException(status_code=404, detail=f"Auto with ID {auto_id} does not exist.")

    # Validate and update price per hour if provided
    if auto_update.preis_pro_stunde is not None:
        if auto_update.preis_pro_stunde <= 0:
            logger.warning("Invalid price per hour during update")
            raise HTTPException(status_code=400, detail="Price per hour must be greater than 0.")
        auto.preis_pro_stunde = auto_update.preis_pro_stunde

    # Update other fields if provided
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
    logger.info(f"Auto with ID {auto_id} updated successfully")
    return auto


@router.post("/autos/{auto_id}/calculate-price")
def calculate_total_price(
    auto_id: int = Path(..., gt=0, description="The ID of the auto (must be > 0)"),
    mietdauer_stunden: int = Query(..., gt=0, description="Rental duration in hours (must be > 0)"),
    db: Session = Depends(get_database_session)
):
    # Calculate total price for rental based on hourly rate and duration
    logger.info(f"Calculating total price for auto ID {auto_id} with rental duration {mietdauer_stunden} hours")

    auto = db.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto:
        logger.warning(f"Auto with ID {auto_id} not available")
        raise HTTPException(status_code=404, detail=f"Auto with ID {auto_id} is not available.")

    if not auto.status:
        logger.warning("Auto currently not available")
        raise HTTPException(status_code=400, detail="The auto is currently not available.")

    if mietdauer_stunden <= 0:
        logger.warning("Invalid rental duration")
        raise HTTPException(status_code=400, detail="Rental duration must be greater than 0.")

    gesamtpreis = auto.preis_pro_stunde * mietdauer_stunden
    logger.info(f"Total price calculated: {gesamtpreis} EUR")
    return {
        "auto_id": auto_id,
        "mietdauer_stunden": mietdauer_stunden,
        "preis_pro_stunde": auto.preis_pro_stunde,
        "gesamtpreis": gesamtpreis
    }


@router.delete("/autos/{auto_id}", status_code=204)
def delete_auto(auto_id: int, db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    # Only 'owner' can delete autos
    check_role(current_user, "owner")
    logger.info(f"Attempting to delete auto with ID: {auto_id}")

    auto = db.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto:
        logger.warning(f"Auto with ID {auto_id} not found for deletion")
        raise HTTPException(status_code=404, detail=f"Auto with ID {auto_id} not found.")

    db.delete(auto)
    db.commit()
    logger.info(f"Auto with ID {auto_id} deleted successfully")
    return
