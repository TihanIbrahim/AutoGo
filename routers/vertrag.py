from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.vertrag import Vertrag as Vertragmodel
from models.auto import Auto
from models.kunden import Kunden
from schemas.vertrag import VertragCreate as VertragSchema , Vertrag
from data_base import get_database_session

router = APIRouter(prefix="/api/v1")

# مسار لإنشاء عقد
@router.post("/vertrag", response_model=Vertrag)

def create_vertrag(vertrag: VertragSchema, db_session: Session = Depends(get_database_session)):
    try:
        beginnt_datum = vertrag.beginnt_datum
        beendet_datum = vertrag.beendet_datum
    except ValueError:
        raise HTTPException(status_code=400, detail="Das Datumsformat ist ungültig. Bitte verwenden Sie das Format TT-MM-JJJJ.")
    
    if beginnt_datum >= beendet_datum:
        raise HTTPException(status_code=400, detail="Beginndatum muss vor dem Enddatum liegen.")
    
    auto = db_session.query(Auto).filter(Auto.id == vertrag.auto_id).first()
    if not auto:
        raise HTTPException(status_code=404, detail="Auto mit dieser ID wurde nicht gefunden.")
    
    if auto.status == False:
        raise HTTPException(status_code=400, detail="Auto ist besetzt.")
    
    auto.status = False
    db_session.commit()
    db_session.refresh(auto)

    kunde = db_session.query(Kunden).filter(Kunden.id == vertrag.kunden_id).first()
    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde mit dieser ID wurde nicht gefunden.")
    
    db_vertrag = Vertragmodel(
        auto_id=vertrag.auto_id,
        kunden_id=vertrag.kunden_id,
        beginnt_datum=beginnt_datum,
        beendet_datum=beendet_datum,
        status=vertrag.status,
        total_prise=vertrag.total_prise
    )
    
    db_session.add(db_vertrag)
    db_session.commit()
    db_session.refresh(db_vertrag)

    if datetime.now().date() >= beendet_datum:
        auto.status = True
        db_session.commit()
        db_session.refresh(auto)
    
    return db_vertrag



@router.post("/vertraege/{vertrag_id}/kuendigen", response_model=dict)
def Vertrag_kündigen(vertrag_id: int, db_session: Session = Depends(get_database_session)):
    
    vertrag_db = db_session.query(Vertragmodel).filter(Vertragmodel.id == vertrag_id).first()
    if not vertrag_db:
        raise HTTPException(status_code=400, detail="Es gibt kein vertrag mit dieser ID-Nummer.")

    
    beginnt_datum = vertrag_db.beginnt_datum

   
    if datetime.now().date() >= beginnt_datum:
        raise HTTPException(status_code=400, detail="Leider konnten Sie den Vertrag nicht kündigen.")
    
   
    if datetime.now().date() < beginnt_datum:
        vertrag_db.status = False 
        db_session.commit()
        return {"message": "Der Vertrag wurde gekündiget"}



def zwischenstatus_aktuliseren(db_session: Session):
    all_vertrag = db_session.query(Vertragmodel).all()
    for vertrag in all_vertrag:
        if vertrag.beendet_datum <= datetime.now().date():
            auto = db_session.query(Auto).filter(Auto.id == vertrag.auto_id).first()
            if auto and auto.status == False:
                auto.status = True
                db_session.commit()
                db_session.refresh(auto)
                vertrag.status = False
                db_session.commit()
