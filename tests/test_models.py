import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_base import Base
from models.auto import Auto
from models.kunden import Kunden
from models.vertrag import Vertrag
from models.zahlung import Zahlung
from models.user import User
from datetime import date
from security.hash import hash_password , verify

# In-memory SQLite setup
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to set up session and database
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Test creating Auto, Kunden, Vertrag, and Zahlung records
def test_create_auto_vertrag_kunde(db):
    auto = Auto(
        brand="BMW",
        model="sedan",
        jahr=2007,
        preis_pro_stunde=30,
        status=True
    )
    db.add(auto)
    db.commit()
    db.refresh(auto)


    kunden = Kunden(
        vorname="Tihan",
        nachname="Ibrahim",
        geb_datum=date(2000, 8, 25),
        handy_nummer="0947698022",
        email="titor9424@gmail.com"
    )
    db.add(kunden)
    db.commit()
    db.refresh(kunden)

    vertrag = Vertrag(
        auto_id=auto.id,
        kunden_id=kunden.id,
        status=True,
        beginnt_datum=date(2000, 5, 25),
        beendet_datum=date(2000, 6, 25),
        total_preis=500
    )
    db.add(vertrag)
    db.commit()
    db.refresh(vertrag)

    zahlung = Zahlung(
        vertragid=vertrag.id,
        zahlungsmethode="direkt überweisung",
        datum=date(2025, 3, 11),
        status="wurde überwiesen",
        betrag=300.0
    )
    db.add(zahlung)
    db.commit()
    db.refresh(zahlung)

    # Assertions
    assert vertrag.id is not None
    assert vertrag.auto_id == auto.id
    assert vertrag.kunden_id == kunden.id
    assert zahlung.vertragid == vertrag.id
    assert auto.brand == "BMW"
    assert vertrag.kunde.vorname == "Tihan"


def test_user(db):
    user=User(
        email = "tihanibrahim@hotmail.com",
        hashed_password = hash_password("123456789tito")
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    
    # Assertions
    assert user.id is not None
    assert user.email == "tihanibrahim@hotmail.com"
    assert verify("123456789tito", user.hashed_password)





    