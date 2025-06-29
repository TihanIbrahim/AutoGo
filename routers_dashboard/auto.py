from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.auto import Auto as AutoModel, AutoStatus
from schemas.auto import AutoCreate, Auto, AutoUpdate
from data_base import get_database_session
from logger_config import setup_logger
from services.dependencies import owner_required, owner_or_editor_required , owner_or_viewer_required
from models.user import User

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/dashboard")

# Hilfsfunktion, um ein Auto anhand der ID zu holen oder 404 Fehler auszulösen
def get_auto_by_id(db: Session, auto_id: int) -> AutoModel:
    auto = db.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto:
        logger.warning(f"Auto mit ID {auto_id} nicht gefunden")  # Auto nicht gefunden
        raise HTTPException(status_code=404, detail=f"Auto mit ID {auto_id} nicht gefunden.")
    return auto

# Stundenpreis validieren: muss größer als 0 sein
def validate_preis_pre_stunde(preis: float):
    if preis <= 0:
        logger.warning("Ungültiger Stundenpreis (<= 0)")  # Ungültiger Stundenpreis
        raise HTTPException(status_code=400, detail="Der Stundenpreis muss größer als 0 sein.")

# =================== Auto erstellen ===================
@router.post("/autos", response_model=Auto, status_code=201)
def create_auto(
    auto: AutoCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Dashboard: Auto wird erstellt: {auto.brand} {auto.model}")
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
    logger.info(f"Dashboard: Auto erfolgreich erstellt mit ID: {db_auto.id}")
    return db_auto

# =================== Auto aktualisieren ===================
@router.put("/autos/{auto_id}", response_model=Auto)
def update_auto(
    auto_id: int,
    auto_update: AutoUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_editor_required)
):
    logger.info(f"Dashboard: Auto mit ID {auto_id} wird aktualisiert")
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
    logger.info(f"Dashboard: Auto mit ID {auto_id} wurde erfolgreich aktualisiert")
    return auto

# =================== Auto löschen ===================
@router.delete("/autos/{auto_id}", status_code=204)
def delete_auto(
    auto_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Dashboard: Löschvorgang für Auto mit ID {auto_id} wird gestartet")
    auto = get_auto_by_id(db, auto_id)

    db.delete(auto)
    db.commit()
    logger.info(f"Dashboard: Auto mit ID {auto_id} wurde erfolgreich gelöscht")
    return

# =================== Alle verfügbaren Autos anzeigen ===================
@router.get("/autos", response_model=List[Auto])
def show_all_auto(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_or_viewer_required)
):
    logger.info("Alle verfügbaren Autos werden abgerufen")  # Alle verfügbaren Autos holen
    autos = db.query(AutoModel).filter(AutoModel.status == AutoStatus.verfügbar).all()
    if not autos:
        logger.info("Keine verfügbaren Autos gefunden")  # Keine Autos verfügbar
    return autos

# =================== Auto anzeigen ===================
@router.get("/autos/{auto_id}", response_model=Auto)
def show_auto(
    auto_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(owner_required)
):
    logger.info(f"Auto mit ID {auto_id} wird angezeigt")  # Auto anzeigen
    auto_details = get_auto_by_id(db, auto_id)
    return auto_details
