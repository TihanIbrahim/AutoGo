from pydantic import ValidationError
from schemas.auto import AutoBase
from schemas.vertrag import VertragBase
from schemas.kunden import KundenBase
from schemas.zahlung import ZahlungBase, ZahlungsStatusEnum, ZahlungsmethodeEnum
from schemas.auth_schemas import CreateRequest, TokenData
import pytest
from datetime import date
import random
import secrets
# ------------------------------
# AutoBase schema tests
# ------------------------------

# Test valid AutoBase schema input
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
    assert auto.status =="verfügbar"

# Combined test for invalid type and missing required field for 'jahr'
def test_invalid_or_missing_auto_schema():
    # Invalid type for 'jahr'
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="sedan",
            jahr="not_a_number",  # Invalid type
            preis_pro_stunde=35,
            status="verfügbar"
        )
    # Missing required field 'jahr'
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="X5",
            preis_pro_stunde=40,
            status="verfügbar"
        )

# ------------------------------
# KundenBase schema tests
# ------------------------------

# Test valid KundenBase schema input
def test_valid_kunde_schema():
    kunde = KundenBase(
        vorname="Tihan",
        nachname="Ibrahim",
        geb_datum=date(2000, 8, 25),
        handy_nummer="0947698022",
        email="titor9424@gmail.com"
    )
    assert kunde.vorname == "Tihan"
    assert kunde.nachname == "Ibrahim"
    assert kunde.geb_datum == date(2000, 8, 25)
    assert kunde.handy_nummer == "0947698022"
    assert kunde.email == "titor9424@gmail.com"

# Combined test for invalid email and missing required fields 'handy_nummer' and 'email'
def test_invalid_or_missing_kunde_schema():
    # Invalid email format
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ibrahim",
            geb_datum=date(2000, 8, 25),
            handy_nummer="0947698022",
            email="invalid_email"  # Invalid email
        )
    # Missing required fields 'handy_nummer' and 'email'
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ali",
            geb_datum=date(2000, 8, 25)
        )

# ------------------------------
# VertragBase schema tests
# ------------------------------

# Test valid VertragBase schema input
def test_valid_vertrag():
    vertrag = VertragBase(
        auto_id=32,
        kunden_id=22,
        beginnt_datum=date(2000, 4, 20),  # Fixed typo here
        beendet_datum=date(2000, 5, 25),
        total_preis=321.2,
        status= "aktiv"
    )
    assert vertrag.auto_id == 32
    assert vertrag.kunden_id == 22
    assert vertrag.beginnt_datum == date(2000, 4, 20)  # Confirmed spelling as in schema
    assert vertrag.beendet_datum == date(2000, 5, 25)
    assert vertrag.total_preis == 321.2
    assert vertrag.status == "aktiv"

# Combined test for invalid type and missing required field for 'kunden_id'
def test_invalid_or_missing_vertrag_schema():
    # Invalid type for 'kunden_id'
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            kunden_id="not a number",  # Invalid type
            beginnt_datum=date(2000, 4, 20),
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status= "aktiv"
        )
    # Missing required field 'kunden_id'
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status= "aktiv"
        )

# ------------------------------
# ZahlungBase schema tests
# ------------------------------

# Test valid ZahlungBase schema input
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

# Combined test for invalid enum values and invalid/missing types in ZahlungBase
def test_invalid_or_missing_zahlung():
    # Invalid enum values and invalid type for 'betrag'
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertrag_id=31,
            zahlungsmethode="direkt überweisung",  # Invalid enum
            datum=date(2025, 3, 11),
            status="wurde überwiesen",  # Invalid enum
            betrag="text"  # Invalid type
        )
    # Missing required field 'datum'
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertrag_id=31,
            zahlungsmethode=ZahlungsmethodeEnum.karte,
            status=ZahlungsStatusEnum.offen,
            betrag=300.0
        )

# ------------------------------
# Auth schema tests
# ------------------------------

# Test valid CreateRequest schema input
def test_valid_request():
    request = CreateRequest(
        email="loloakiL@gmail.com",
        password="Abc123456!"
    )
    assert request.email == "loloakiL@gmail.com"
    assert request.password == "Abc123456!"

# Combined test for invalid email/password format and missing password
def test_invalid_or_missing_request():
    
    random_num = secrets.randbelow(100000) + 1
    with pytest.raises(ValidationError):
        CreateRequest(
            email=f"user{random_num}@gmail.com",
            password="123456789"
        )
    # Missing password field
    with pytest.raises(ValidationError):
        CreateRequest(
            email="loloakiL@gmail.com"
        )

# Test valid password meeting all rules
def test_valid_password():
    request = CreateRequest(email="test@example.com", password="Abcd1234!")
    assert request.password == "Abcd1234!"

# Test password too short
def test_password_too_short():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="A1b!")

# Test password missing uppercase letter
def test_password_missing_uppercase():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="abcd1234!")

# Test password missing special character
def test_password_missing_special_char():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="Abcd1234")

# Test password missing digit
def test_password_missing_digit():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="Abcdefg!")

# ------------------------------
# TokenData schema tests
# ------------------------------

# Test valid TokenData input
def test_valid_token_data():
    token = TokenData(email="user@example.com", id=1)
    assert token.email == "user@example.com"
    assert token.id == 1

# Test invalid email format in TokenData
def test_invalid_email():
    with pytest.raises(ValidationError):
        TokenData(email="invalid-email", id=1)

# Test invalid id type in TokenData
def test_invalid_id_type():
    with pytest.raises(ValidationError):
        TokenData(email="user@example.com", id="not_an_int")
