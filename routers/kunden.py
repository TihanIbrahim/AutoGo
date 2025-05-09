from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from data_base import get_database_session
from models.kunden import Kunden as kundenmodel
from schemas.kunden import KundenCreate, Kunden
from fastapi import status

router = APIRouter(prefix="/api/v1")

@router.post("/kunde", response_model=Kunden)
def create_kunden(kunden: KundenCreate, db_session: Session = Depends(get_database_session)):
    # إنشاء كائن الزبون وتخزينه في قاعدة البيانات
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
    
    return db_kunden

@router.delete("/kunde/{kunden_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kunde(kunden_id: int, db: Session = Depends(get_database_session)):
    # البحث عن العميل في قاعدة البيانات
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    # حذف العميل من قاعدة البيانات
    db.delete(kunde)
    db.commit()

    return None  # تأكد من أن العودة لا تحتوي على أي محتوى.

@router.get("/kunde/{kunden_id}", response_model=Kunden)
def get_kunde(kunden_id: int, db: Session = Depends(get_database_session)):
    # البحث عن العميل في قاعدة البيانات
    kunde = db.query(kundenmodel).filter(kundenmodel.id == kunden_id).first()

    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    return kunde
