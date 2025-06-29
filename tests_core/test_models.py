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

# Verwendung einer In-Memory SQLite-Datenbank zum Testen, um Nebeneffekte auf die echte DB zu vermeiden
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Erstellung einer konfigurierten Session-Klasse für die DB-Verbindung
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pytest Fixture zum Setup und Teardown der Datenbank für jeden Test
@pytest.fixture(scope="function")
def db():
    # Erstelle alle Tabellen in der Testdatenbank vor jedem Test
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db  # Übergibt die Session an den Test
    finally:
        # Schließe die Session und lösche alle Tabellen nach dem Test zur Bereinigung
        db.close()
        Base.metadata.drop_all(bind=engine)

# Test zur Erstellung von Auto, Kunden, Vertrag und Zahlung
def test_create_auto_vertrag_kunde(db):
    # Erstelle und füge ein Auto-Objekt hinzu
    auto = Auto(
        brand="BMW",
        model="sedan",
        jahr=2007,
        preis_pro_stunde=30,
        status=AutoStatus.verfügbar  # Auto ist verfügbar
    )
    db.add(auto)
    db.commit()
    db.refresh(auto)  # Aktualisiert das Objekt, um z.B. die DB-generierte ID zu erhalten

    # Erstelle und füge einen Kunden hinzu
    kunden = Kunden(
        vorname="Tihan",
        nachname="Ibrahim",
        geb_datum=date(2000, 8, 25),
        handy_nummer="0934556611",
        email="titor9424@gmail.com"
    )
    db.add(kunden)
    db.commit()
    db.refresh(kunden)

    # Erstelle und füge einen Vertrag ein, der Auto und Kunden verbindet
    vertrag = Vertrag(
        auto_id=auto.id,
        kunden_id=kunden.id,
        status="aktiv",
        beginnt_datum=date(2000, 5, 25),
        beendet_datum=date(2000, 6, 25),
        total_preis=500
    )
    db.add(vertrag)
    db.commit()
    db.refresh(vertrag)

    # Erstelle und füge eine Zahlung hinzu, die mit dem Vertrag verknüpft ist
    zahlung = Zahlung(
        vertrag_id=vertrag.id,
        zahlungsmethode=ZahlungsmethodeEnum.karte,
        datum=date(2025, 3, 11),
        status=ZahlungsStatusEnum.bezahlt,
        betrag=300.0
    )
    db.add(zahlung)
    db.commit()
    db.refresh(zahlung)

    # Prüfungen, ob die Daten korrekt erstellt wurden
    assert vertrag.id is not None  # Vertrag hat eine ID erhalten
    assert vertrag.auto_id == auto.id  # Vertrag verweist auf korrektes Auto
    assert vertrag.kunden_id == kunden.id  # Vertrag verweist auf korrekten Kunden
    assert zahlung.vertrag_id == vertrag.id  # Zahlung ist mit dem Vertrag verknüpft
    assert auto.brand == "BMW"  # Überprüfung der Automarke
    assert vertrag.kunde.vorname == "Tihan"  # Zugriff auf Kunden-Relation im Vertrag

# Test zur Erstellung eines Users sowie Passwort-Hashing und Verifikation
def test_user(db):
    # Erstelle einen Benutzer mit gehashtem Passwort
    user = User(
        email="tihanibrahim@hotmail.com",
        hashed_password=hash_password("123456789tito")
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Prüfungen zur Validierung der User-Erstellung und Passwortüberprüfung
    assert user.id is not None  # User hat eine ID erhalten
    assert user.email == "tihanibrahim@hotmail.com"  # Email stimmt überein
    assert verify("123456789tito", user.hashed_password)  # Passwortprüfung erfolgreich
    assert user.role == "customer"  # Standardrolle ist "customer" (sofern im Model definiert)
