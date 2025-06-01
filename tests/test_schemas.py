from pydantic import ValidationError
from schemas.auto import AutoBase
from schemas.vertrag import VertragBase
from schemas.kunden import KundenBase
from schemas.zahlung import ZahlungBase
from schemas.auth_schemas import CreateRequest, TokenData
import pytest
from datetime import date
import random

# ------------------------------
# AutoBase schema tests
# ------------------------------

# Valid AutoBase input
def test_valid_auto_schema():
    auto = AutoBase(
        brand="BMW",
        model="sedan",
        jahr=2006,
        preis_pro_stunde=35,
        status=True
    )
    assert auto.brand == "BMW"
    assert auto.model == "sedan"
    assert auto.jahr == 2006
    assert auto.preis_pro_stunde == 35
    assert auto.status is True

# Invalid type for jahr (should be int)
def test_invalid_auto_schema():
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="sedan",
            jahr="not_a_number",
            preis_pro_stunde=35,
            status=True
        )

# Missing required field 'jahr'
def test_missing_field_auto_schema():
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="X5",
            preis_pro_stunde=40,
            status=True
        )

# ------------------------------
# KundenBase schema tests
# ------------------------------

# Valid KundenBase input
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

# Invalid email format
def test_invalid_kunde_schema():
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ibrahim",
            geb_datum=date(2000, 8, 25),
            handy_nummer="0947698022",
            email="invalid_email"
        )

# Missing fields: handy_nummer and email
def test_missing_field_kunde_schema():
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ali",
            geb_datum=date(2000, 8, 25)
        )

# ------------------------------
# VertragBase schema tests
# ------------------------------

# Valid VertragBase input
def test_valid_vertrag():
    vertrag = VertragBase(
        auto_id=32,
        kunden_id=22,
        beginnt_datum=date(2000, 4, 20),
        beendet_datum=date(2000, 5, 25),
        total_preis=321.2,
        status=True
    )
    assert vertrag.auto_id == 32
    assert vertrag.kunden_id == 22
    assert vertrag.beginnt_datum == date(2000, 4, 20)
    assert vertrag.beendet_datum == date(2000, 5, 25)
    assert vertrag.total_preis == 321.2
    assert vertrag.status is True

# Invalid kunden_id (should be int)
def test_invalid_vertrag_schema():
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            kunden_id="not a number",
            beginnt_datum=date(2000, 4, 20),
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status=True
        )

# Missing required field 'kunden_id'
def test_missing_field_vertrag_schema():
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status=True
        )

# ------------------------------
# ZahlungBase schema tests
# ------------------------------

# Valid ZahlungBase input
def test_valid_zahlung():
    zahlung = ZahlungBase(
        vertragid=31,
        zahlungsmethode="direkt überweisung",
        datum=date(2025, 3, 11),
        status="wurde überwiesen",
        betrag=300.0
    )
    assert zahlung.vertragid == 31
    assert zahlung.zahlungsmethode == "direkt überweisung"
    assert zahlung.datum == date(2025, 3, 11)
    assert zahlung.status == "wurde überwiesen"
    assert zahlung.betrag == 300.0

# Invalid type for betrag (should be float)
def test_invalid_zahlung():
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertragid=31,
            zahlungsmethode="direkt überweisung",
            datum=date(2025, 3, 11),
            status="wurde überwiesen",
            betrag="text"
        )

# Missing required field 'datum'
def test_missing_field_zahlung():
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertragid=31,
            zahlungsmethode="direkt überweisung",
            status="wurde überwiesen",
            betrag=300.0
        )

# ------------------------------
# Auth schema tests
# ------------------------------

# Valid CreateRequest input
def test_valid_request():
    request = CreateRequest(
        email="loloakiL@gmail.com",
        password="Abc123456!"
    )
    assert request.email == "loloakiL@gmail.com"
    assert request.password == "Abc123456!"

# Invalid email format
def test_invalid_request():
    with pytest.raises(ValidationError):
        CreateRequest(
            email=f"user{random.randint(1,100000)}@gmail.com",
            password="123456789"
        )

# Missing password field
def test_missing_field_request():
    with pytest.raises(ValidationError):
        CreateRequest(
            email="loloakiL@gmail.com"
        )

# Valid password with all required rules
def test_valid_password():
    request = CreateRequest(email="test@example.com", password="Abcd1234!")
    assert request.password == "Abcd1234!"

# Password too short
def test_password_too_short():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="A1b!")

# Password missing uppercase letter
def test_password_missing_uppercase():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="abcd1234!")

# Password missing special character
def test_password_missing_special_char():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="Abcd1234")

# Password missing digit
def test_password_missing_digit():
    with pytest.raises(ValidationError):
        CreateRequest(email="test@example.com", password="Abcdefg!")



def test_valid_token_data():
    # Test with valid email and id
    token = TokenData(email="user@example.com", id=1)
    assert token.email == "user@example.com"
    assert token.id == 1

def test_invalid_email():
    # Test with invalid email format, should raise ValidationError
    with pytest.raises(ValidationError):
        TokenData(email="invalid-email", id=1)

def test_invalid_id_type():
    # Test with invalid id type (string instead of int), should raise ValidationError
    with pytest.raises(ValidationError):
        TokenData(email="user@example.com", id="not_an_int")