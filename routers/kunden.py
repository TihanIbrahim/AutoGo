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

# Create a new customer (allowed for Customers only)
@router.post("/kunde", response_model=Kunden, status_code=201)
def create_kunden(
    kunden: KundenCreate,
    db_session: Session = Depends(get_database_session),
    current_user: User = Depends(customer_required)  # Only customer role allowed
):
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

# List all customers (allowed for Owners only)
@router.get("/kunden", response_model=List[Kunden])
def show_all_kunden(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owner role allowed
):
    logger.info("Alle Kunden werden abgerufen")
    kunden = db.query(kundenmodel).all()
    return kunden

# Delete a customer by ID (allowed for Owners only)
@router.delete("/kunden/{kunden_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kunde(
    kunden_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owner role allowed
):
    logger.info(f"Versuche, Kunde mit ID {kunden_id} zu löschen")
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunden_id} nicht gefunden.")

    db.delete(kunde)
    db.commit()
    logger.info(f"Kunde mit ID {kunden_id} erfolgreich gelöscht")
    return None

# Get customer details by ID (allowed for Owners only)
@router.get("/kunden/{kunden_id}", response_model=Kunden)
def get_kunde(
    kunden_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owner role allowed
):
    logger.info(f"Kunde mit ID {kunden_id} wird abgerufen")
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunden_id} nicht gefunden.")

    return kunde

# Update customer details by ID (allowed for Owners only)
@router.put("/kunden/{kunden_id}", response_model=Kunden)
def update_kunde(
    kunden_id: int,
    kunde_update: KundenUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Only owner role allowed
):
    logger.info(f"Aktualisiere Kunde mit ID: {kunden_id}")
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunden_id} nicht gefunden.")

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
