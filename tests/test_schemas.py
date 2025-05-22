from pydantic import ValidationError
from schemas.auto import AutoBase
from schemas.vertrag import VertragBase
from schemas.kunden import KundenBase
from schemas.zahlung import ZahlungBase
import pytest
from datetime import date

# ------------------------------
# AutoBase schema tests
# ------------------------------

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

def test_invalid_auto_schema():
    # jahr should be int, not string
    with pytest.raises(ValidationError):
        AutoBase(
            brand="BMW",
            model="sedan",
            jahr="not_a_number",
            preis_pro_stunde=35,
            status=True
        )

def test_missing_field_auto_schema():
    # Missing 'jahr'
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

def test_invalid_kunde_schema():
    # Invalid email format
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ibrahim",
            geb_datum=date(2000, 8, 25),
            handy_nummer="0947698022",
            email="invalid_email"
        )

def test_missing_field_kunde_schema():
    # Missing 'handy_nummer' and 'email'
    with pytest.raises(ValidationError):
        KundenBase(
            vorname="Tihan",
            nachname="Ali",
            geb_datum=date(2000, 8, 25)
        )

# ------------------------------
# VertragBase schema tests
# ------------------------------

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

def test_invalid_vertrag_schema():
    # kunden_id should be int, not string
    with pytest.raises(ValidationError):
        VertragBase(
            auto_id=32,
            kunden_id="not a number",
            beginnt_datum=date(2000, 4, 20),
            beendet_datum=date(2000, 5, 25),
            total_preis=321.2,
            status=True
        )

def test_missing_field_vertrag_schema():
    # Missing 'kunden_id'
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

def test_invalid_zahlung():
    # betrag should be float, not string
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertragid=31,
            zahlungsmethode="direkt überweisung",
            datum=date(2025, 3, 11),
            status="wurde überwiesen",
            betrag="text"
        )

def test_missing_field_zahlung():
    # Missing 'datum'
    with pytest.raises(ValidationError):
        ZahlungBase(
            vertragid=31,
            zahlungsmethode="direkt überweisung",
            status="wurde überwiesen",
            betrag=300.0
        )





  

    