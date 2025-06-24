import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_base import Base
from models.auto import Auto , AutoStatus
from models.kunden import Kunden
from models.vertrag import Vertrag
from models.zahlung import Zahlung , ZahlungsmethodeEnum , ZahlungsStatusEnum
from models.user import User
from datetime import date
from security.hash import hash_password, verify

# Use in-memory SQLite database for testing purposes to avoid side effects on real DB
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pytest fixture to setup and teardown the database for each test function
@pytest.fixture(scope="function")
def db():
    # Create all tables in the test database before each test
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db  # Provide the session to the test
    finally:
        # Close session and drop all tables after the test runs to clean up
        db.close()
        Base.metadata.drop_all(bind=engine)

# Test creating records for Auto, Kunden (Customer), Vertrag (Contract), and Zahlung (Payment)
def test_create_auto_vertrag_kunde(db):
    # Create and add a car (Auto) instance
    auto = Auto(
        brand="BMW",
        model="sedan",
        jahr=2007,
        preis_pro_stunde=30,
        status=AutoStatus.verfügbar # True means available
    )
    db.add(auto)
    db.commit()
    db.refresh(auto)  # Refresh to get the generated ID and other DB-set fields

    # Create and add a customer (Kunden) instance
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

    # Create and add a contract (Vertrag) linking Auto and Kunden
    vertrag = Vertrag(
        auto_id=auto.id,
        kunden_id=kunden.id,
        status= "aktiv",
        beginnt_datum=date(2000, 5, 25),
        beendet_datum=date(2000, 6, 25),
        total_preis=500
    )
    db.add(vertrag)
    db.commit()
    db.refresh(vertrag)

    # Create and add a payment (Zahlung) linked to the contract
    zahlung = Zahlung(
        vertrag_id =vertrag.id,
        zahlungsmethode=ZahlungsmethodeEnum.karte,
        datum=date(2025, 3, 11),
        status=ZahlungsStatusEnum.bezahlt,
        betrag=300.0
    )
    
    db.add(zahlung)
    db.commit()
    db.refresh(zahlung)

    # Assertions to verify that data is created correctly
    assert vertrag.id is not None  # Contract ID should be assigned by DB
    assert vertrag.auto_id == auto.id  # Contract's car ID matches created car
    assert vertrag.kunden_id == kunden.id  # Contract's customer ID matches created customer
    assert zahlung.vertrag_id == vertrag.id  # Payment linked to correct contract
    assert auto.brand == "BMW"  # Car brand check
    assert vertrag.kunde.vorname == "Tihan"  # Customer's first name via relationship

# Test user creation and password hashing + verification
def test_user(db):
    # Create a user with hashed password
    user = User(
        email="tihanibrahim@hotmail.com",
        hashed_password=hash_password("123456789tito")
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assertions to verify user creation and password check
    assert user.id is not None  # User ID assigned by DB
    assert user.email == "tihanibrahim@hotmail.com"  # Email matches
    assert verify("123456789tito", user.hashed_password)  # Password verification should succeed
    assert user.role == "customer"  # Default role check (assuming default set in model)

    