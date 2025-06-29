from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from typing import List
from data_base import get_database_session
from models.kunden import Kunden as KundenModel
from schemas.kunden import KundenCreate, Kunden, KundenUpdate
from logger_config import setup_logger
from models.user import User
from services.dependencies import (
    owner_required,
    owner_or_editor_required,
    owner_or_viewer_required,
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/dashboard")

# Hilfsfunktion, um einen Kunden anhand der ID zu holen oder 404 Fehler auszulösen
def get_kunde_by_id(db: Session, kunden_id: int) -> KundenModel:
    kunde = db.query(KundenModel).filter(KundenModel.id == kunden_id).first()
    if not kunde:
        logger.warning(f"Kunde mit ID {kunden_id} nicht gefunden")  # Kunde nicht gefunden
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunden_id} nicht gefunden.")
    return kunde

# =================== Neuen Kunden erstellen ===================
@router.post("/kunden", response_model=Kunden, status_code=201)
def create_kunde(
    kunde: KundenCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Nur Besitzer dürfen erstellen
):
    logger.info(f"Dashboard: Neuer Kunde wird erstellt: {kunde.vorname} {kunde.nachname}")
    db_kunde = KundenModel(
        vorname=kunde.vorname,
        nachname=kunde.nachname,
        geb_datum=kunde.geb_datum,
        handy_nummer=kunde.handy_nummer,
        email=kunde.email
    )
    db.add(db_kunde)
    db.commit()
    db.refresh(db_kunde)
    logger.info(f"Dashboard: Kunde erfolgreich erstellt mit ID: {db_kunde.id}")
    return db_kunde

# =================== Alle Kunden abrufen ===================
@router.get("/kunden", response_model=List[Kunden])
def get_all_kunden(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_viewer_required)  # Besitzer und Viewer zugelassen
):
    logger.info("Dashboard: Alle Kunden werden abgerufen")
    kunden = db.query(KundenModel).all()
    if not kunden:
        logger.info("Dashboard: Keine Kunden gefunden")
    return kunden

# =================== Kunden Details abrufen ===================
@router.get("/kunden/{kunden_id}", response_model=Kunden)
def get_kunde_details(
    kunden_id: int = Path(..., gt=0, description="Die ID des Kunden (muss > 0 sein)"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Nur Besitzer dürfen Details sehen
):
    logger.info(f"Dashboard: Abruf von Kunde mit ID {kunden_id}")
    kunde = get_kunde_by_id(db, kunden_id)
    return kunde

# =================== Kunden aktualisieren ===================
@router.put("/kunden/{kunden_id}", response_model=Kunden)
def update_kunde(
    kunden_id: int,
    kunde_update: KundenUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_editor_required)  # Besitzer oder Editor zugelassen
):
    logger.info(f"Dashboard: Aktualisierung von Kunde mit ID {kunden_id}")
    kunde = get_kunde_by_id(db, kunden_id)

    # Nur vorhandene Felder aktualisieren
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
    logger.info(f"Dashboard: Kunde mit ID {kunden_id} erfolgreich aktualisiert")
    return kunde

# =================== Kunden löschen ===================
@router.delete("/kunden/{kunden_id}", status_code=204)
def delete_kunde(
    kunden_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)  # Nur Besitzer dürfen löschen
):
    logger.info(f"Dashboard: Löschvorgang für Kunde mit ID {kunden_id} wird gestartet")
    kunde = get_kunde_by_id(db, kunden_id)
    db.delete(kunde)
    db.commit()
    logger.info(f"Dashboard: Kunde mit ID {kunden_id} wurde erfolgreich gelöscht")
    return
