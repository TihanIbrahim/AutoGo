import pytest
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker ,session
from data_base import Base
from models.auto import Auto
from models.kunden import Kunden
from models.vertrag import Vertrag
from datetime import date

# إعداد قاعدة البيانات داخل الذاكرة
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# fixture لتجهيز الجلسة وقاعدة البيانات
@pytest.fixture(scope="function")
def db() :
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)




def test_create_auto_vertrag_kunde(db):
    auto = Auto(
        brand="BMW",
        model="sedan",
        jahr=2007,
        preis_pro_stunde=30,
        status=True
    )
    db.add(auto)

    kunden = Kunden(
        vorname="Tihan",
        nachname="Ibrahim",
        geb_datum=date(2000, 8, 25),
        handy_nummer="0947698022",
        email="titor9424@gmail.com"
    )
    db.add(kunden)
    db.commit()

    vertrag = Vertrag(
        auto_id=auto.id,
        kunden_id=kunden.id,
        status=True,
        beginnt_datum=date(2000, 5, 25),
        beendet_datum=date(2000, 6, 25),
        total_prise="500"
    )
    db.add(vertrag)
    db.commit()
    db.refresh(vertrag)

    assert vertrag.id is not None
    assert vertrag.auto_id == auto.id
    assert vertrag.kunden_id == kunden.id
    assert auto.brand == "BMW"

    # تحقق من العلاقة، بشرط أن تكون معرّفة في نموذج Vertrag
    assert vertrag.kunde.vorname == "Tihan"
