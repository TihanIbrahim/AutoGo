import pytest
from pydantic import ValidationError
from datetime import date
import secrets

from schemas.auto import AutoBase
from schemas.vertrag import VertragBase
from schemas.kunden import KundenBase
from schemas.zahlung import ZahlungBase, ZahlungsStatusEnum, ZahlungsmethodeEnum
from schemas.auth_schemas import CreateRequest, TokenData




# ------------------------------
# Tests für AutoBase-Schema
# ------------------------------

# Test für gültige AutoBase-Daten
def test_valid_auto_schema():
    auto = AutoBase(
        brand="BMW",
        model="sedan",
        jahr=2006,
        preis_pro_stunde=35,
        status= "verfügbar"
    )
    assert auto.brand == "BMW"
    assert auto.model == "sedan"
    assert auto.jahr == 2006
    assert auto.preis_pro_stunde == 35
    assert auto.status == "verfügbar"

# Kombinierter Test für ungültigen Typ und fehlendes Pflichtfeld 'jahr'
def test_invalid_or_missing_auto_schema():
    # Ungültiger Typ für 'jahr'
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="sedan",
            jahr="not_a_number",  # Falscher Typ
            preis_pro_stunde=35,
            status="verfügbar"
        )
    # Fehlendes Pflichtfeld 'jahr'
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="X5",
            preis_pro_stunde=40,
            status="verfügbar"
        )

# ------------------------------
# Tests für KundenBase-Schema
# ------------------------------

# Test für gültige KundenBase-Daten
def test_valid_kunde_schema():
    kunde = KundenBase(
        vorname="Tihan",
        nachname="Ibrahim",
        geb_datum=date(2000, 8, 25),
        handy_nummer="0900000000",
        email="titor9424@gmail.com"
    )
    assert kunde.vorname == "Tihan"
    assert kunde.nachname == "Ibrahim"
    assert kunde.geb_datum == date(2000, 8, 25)
    assert kunde.handy_nummer == "0900000000"
    assert kunde.email == "titor9424@gmail.com"

# Kombinierter Test für ungültige Email und fehlende Pflichtfelder 'handy_nummer' und 'email'
def test_invalid_or_missing_kunde_schema():
    # Ungültiges Email-Format
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ibrahim",
            geb_datum=date(2000, 8, 25),
            handy_nummer="0900000000",
            email="invalid_email"  # Ungültige Email
        )
    # Fehlende Pflichtfelder 'handy_nummer' und 'email'
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ali",
            geb_datum=date(2000, 8, 25)
        )

# ------------------------------
# Tests für VertragBase-Schema
# ------------------------------

# Test für gültige VertragBase-Daten
def test_valid_vertrag():
    vertrag = VertragBase(
        auto_id=32,
        kunden_id=22,
        beginnt_datum=date(2000, 4, 20),
        beendet_datum=date(2000, 5, 25),
        total_preis=321.2,
        status="aktiv"
    )
    assert vertrag.auto_id == 32
    assert vertrag.kunden_id == 22
    assert vertrag.beginnt_datum == date(2000, 4, 20)
    assert vertrag.beendet_datum == date(2000, 5, 25)
    assert vertrag.total_preis == 321.2
    assert vertrag.status == "aktiv"

# Kombinierter Test für ungültigen Typ und fehlendes Pflichtfeld 'kunden_id'
def test_invalid_or_missing_vertrag_schema():
    # Ungültiger Typ für 'kunden_id'
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            kunden_id="not a number",  # Falscher Typ
            beginnt_datum=date(2000, 4, 20),
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status="aktiv"
        )
    # Fehlendes Pflichtfeld 'kunden_id'
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status="aktiv"
        )

# ------------------------------
# Tests für ZahlungBase-Schema
# ------------------------------

# Test für gültige ZahlungBase-Daten
def test_valid_zahlung():
    zahlung = ZahlungBase(
        vertrag_id=31,
        zahlungsmethode=ZahlungsmethodeEnum.karte,
        datum=date(2025, 3, 11),
        status=ZahlungsStatusEnum.offen,
        betrag=300.0
    )
    assert zahlung.vertrag_id == 31
    assert zahlung.zahlungsmethode == ZahlungsmethodeEnum.karte
    assert zahlung.datum == date(2025, 3, 11)
    assert zahlung.status == ZahlungsStatusEnum.offen
    assert zahlung.betrag == 300.0

# Kombinierter Test für ungültige Enum-Werte und fehlerhafte Typen bzw. fehlende Felder
def test_invalid_or_missing_zahlung():
    # Ungültige Enum-Werte und falscher Typ für 'betrag'
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertrag_id=31,
            zahlungsmethode="direkt überweisung",  # Ungültiger Enum-Wert
            datum=date(2025, 3, 11),
            status="wurde überwiesen",  # Ungültiger Enum-Wert
            betrag="text"  # Falscher Typ
        )
    # Fehlendes Pflichtfeld 'datum'
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertrag_id=31,
            zahlungsmethode=ZahlungsmethodeEnum.karte,
            status=ZahlungsStatusEnum.offen,
            betrag=300.0
        )

# ------------------------------
# Tests für Auth-Schemas
# ------------------------------

# Test für gültige CreateRequest-Daten
def test_valid_request():
    request = CreateRequest(
        email="loloakiL@gmail.com",
        password="Test-password-1@"
    )
    assert request.email == "loloakiL@gmail.com"
    assert request.password == "Test-password-1@"

# Kombinierter Test für ungültiges Email-/Passwortformat und fehlendes Passwort
def test_invalid_or_missing_request():
    random_num = secrets.randbelow(100000) + 1
    with pytest.raises(ValidationError):
        CreateRequest(
            email=f"user{random_num}@gmail.com",
            password="123456789"  # Passwort entspricht nicht den Anforderungen
        )
    # Fehlendes Passwortfeld
    with pytest.raises(ValidationError):
        CreateRequest(
            email="loloakiL@gmail.com"
        )

# Test für gültiges Passwort (alle Regeln erfüllt)
def test_valid_password():
    request = CreateRequest(email="test@example.com", password="Test-password-1@")
    assert request.password == "Test-password-1@"

# Test für zu kurzes Passwort
def test_password_too_short():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="A1b!")

# Test für Passwort ohne Großbuchstaben
def test_password_missing_uppercase():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="abcd1234!")

# Test für Passwort ohne Sonderzeichen
def test_password_missing_special_char():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="Abcd1234")

# Test für Passwort ohne Ziffer
def test_password_missing_digit():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="Abcdefg!")

# ------------------------------
# Tests für TokenData-Schema
# ------------------------------

# Test für gültige TokenData-Daten
def test_valid_token_data():
    token = TokenData(email="user@example.com", id=1)
    assert token.email == "user@example.com"
    assert token.id == 1

# Test für ungültiges Email-Format in TokenData
def test_invalid_email():
    with pytest.raises(ValidationError):
        TokenData(email="invalid-email", id=1)

# Test für ungültigen Typ des Feldes 'id' in TokenData
def test_invalid_id_type():
    with pytest.raises(ValidationError):
        TokenData(email="user@example.com", id="not_an_int")
