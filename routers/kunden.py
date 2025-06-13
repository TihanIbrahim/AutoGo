from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from data_base import get_database_session
from models.kunden import Kunden as kundenmodel
from schemas.kunden import KundenCreate, Kunden, KundenUpdate
from logger_config import setup_logger
from typing import List
from models.user import User
from services.dependencies import get_current_user, owner_required, customer_required

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1")

# =================== Kunde abrufen ===================
def get_kunde(db: Session, kunden_id: int) -> kundenmodel:
    # Retrieve customer from database by ID, raise 404 if not found
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()
    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunden_id} nicht gefunden.")
    return kunde

# =================== Kunde erstellen ===================
@router.post("/kunde", response_model=Kunden, status_code=201)
def create_kunden(
    kunden: KundenCreate,
    db_session: Session = Depends(get_database_session),
    current_user: User = Depends(customer_required)  # Only customers allowed
):
    # Log and create a new customer in the database
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

# =================== Alle Kunden anzeigen ===================
@router.get("/kunden", response_model=List[Kunden])
def show_all_kunden(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owners allowed
):
    # Retrieve and return all customers from the database
    logger.info("Alle Kunden werden abgerufen")
    kunden = db.query(kundenmodel).all()
    return kunden

# =================== Kunde löschen ===================
@router.delete("/kunden/{kunden_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kunde(
    kunden_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owners allowed
):
    # Delete customer from database if exists, raise 404 if not found
    logger.info(f"Versuche, Kunde mit ID {kunden_id} zu löschen")
    kunde = get_kunde(db, kunden_id)

    db.delete(kunde)
    db.commit()
    logger.info(f"Kunde mit ID {kunden_id} erfolgreich gelöscht")
    return None

# =================== Kundendetails abrufen ===================
@router.get("/kunden/{kunden_id}", response_model=Kunden)
def get_kunde_details(
    kunden_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owners allowed
):
    # Retrieve and return customer details by ID
    logger.info(f"Kunde mit ID {kunden_id} wird abgerufen")
    kunde = get_kunde(db, kunden_id)
    return kunde

# =================== Kunde aktualisieren ===================
@router.put("/kunden/{kunden_id}", response_model=Kunden)
def update_kunde(
    kunden_id: int,
    kunde_update: KundenUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owners allowed
):
    # Update customer information with provided data, raise 404 if not found
    logger.info(f"Aktualisiere Kunde mit ID: {kunden_id}")
    kunde = get_kunde(db, kunden_id)

    if kunde_update.vorname is not None:
        kunde.vorname = kunde_update.vorname
    if kunde_update.nachname is not None:
        kunde.nachname = kunde_update.nachname
    if kunde_update.geb_datum is not None:
        kunde.geb_datum = kunde_update.geb_datum
    if kunde_update.handy_nummer is not None:
        kunde.handy_nummer = kunde_update.handy_nummer
    if kunde_update.email is not None:
        kunde.email = kunde_update.email

    db.commit()
    db.refresh(kunde)
    logger.info(f"Kunde mit ID {kunden_id} erfolgreich aktualisiert")
    return kunde
