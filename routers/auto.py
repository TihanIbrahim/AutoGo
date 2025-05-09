from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from models.auto import Auto as AutoModel
from schemas.auto import AutoCreate, Auto  
from data_base import get_database_session

router = APIRouter(prefix="/api/v1")


@router.post("/auto", response_model=Auto)
def create_auto(auto: AutoCreate, db_session: Session = Depends(get_database_session)):
    db_auto = AutoModel(
        brand=auto.brand,
        model=auto.model,
        jahr=auto.jahr,
        preis_pro_stunde=auto.preis_pro_stunde,
        status=auto.status,
    )
    db_session.add(db_auto)
    db_session.commit()
    db_session.refresh(db_auto)
    return db_auto


@router.get("/autos", response_model=List[Auto])
def show_all_auto(db_session: Session = Depends(get_database_session)):
    return db_session.query(AutoModel).filter(AutoModel.status == True).all()


@router.get("/auto/search", response_model=List[Auto])
def search_auto(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    jahr: Optional[int] = None,
    db: Session = Depends(get_database_session)
):
    query = db.query(AutoModel)
    if brand:
        query = query.filter(AutoModel.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(AutoModel.model.ilike(f"%{model}%"))
    if jahr:
        query = query.filter(AutoModel.jahr == jahr)

    result = query.all()
    if not result:
        raise HTTPException(status_code=404, detail="Keine passenden Autos gefunden.")
    return result


@router.get("/auto/{auto_id}", response_model=Auto)
def show_auto(auto_id: int, db_session: Session = Depends(get_database_session)):
    auto_details = db_session.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto_details:
        raise HTTPException(status_code=404, detail="Auto nicht gefunden.")
    return auto_details



@router.post("/auto/{id}/calculate-price")
def gesamt_preis(
    auto_id: int = Path(..., gt=0),
    mietdauer_stunden: int = Path(..., gt=0),
    db_session: Session = Depends(get_database_session)
):
    auto = db_session.query(AutoModel).filter(AutoModel.id == auto_id).first()
    if not auto:
        raise HTTPException(status_code=404, detail="Auto ist nicht vorhanden")
    if not auto.status:
        raise HTTPException(status_code=400, detail="Das Auto ist nicht zur Vermietung verfügbar")

    gesamtpreis = auto.preis_pro_stunde * mietdauer_stunden

    return {
        "auto_id": auto_id,
        "mietdauer_stunden": mietdauer_stunden,
        "preis_pro_stunde": auto.preis_pro_stunde,
        "gesamtpreis": gesamtpreis
    }

