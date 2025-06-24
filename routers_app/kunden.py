from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from data_base import get_database_session
from models.kunden import Kunden as kundenmodel
from schemas.kunden import KundenCreate, Kunden
from logger_config import setup_logger
from models.user import User
from services.dependencies import customer_or_guest_required

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

# =================== Retrieve customer ===================
def get_kunde(db: Session, kunden_id: int) -> kundenmodel:
    # Retrieve customer by ID, raise 404 if not found
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()
    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunden_id} nicht gefunden.")
    return kunde

# =================== Create customer ===================
@router.post("/kunden", response_model=Kunden, status_code=201)
def create_kunden(
    kunden: KundenCreate,
    db_session: Session = Depends(get_database_session),
    current_user: User = Depends(customer_or_guest_required)  # Only customers allowed
):
    # Log creation and add new customer to the database
    logger.info(f"Erstelle Kunde: {kunden.vorname} {kunden.nachname}")
    db_kunden = kundenmodel(
        vorname=kunden.vorname,
        nachname=kunden.nachname,
        geb_datum=kunden.geb_datum,
        handy_nummer=kunden.handy_nummer,
        email=kunden.email
    )
    db_session.add(db_kunden)
    db_session.commit()
    db_session.refresh(db_kunden)
    logger.info(f"Kunde erfolgreich erstellt mit ID: {db_kunden.id}")
    return db_kunden

