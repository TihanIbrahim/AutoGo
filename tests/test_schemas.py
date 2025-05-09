from pydantic import ValidationError
from schemas.auto import AutoBase
from schemas.vertrag import VertragBase
from schemas.kunden import KundenBase
import pytest
from datetime import date

# ------------------------------
# Tests for AutoBase schema
# ------------------------------

def test_valid_auto_schema():
    data = {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2006,
        "preis_pro_stunde": 35,
        "status": True
    }
    auto = AutoBase(**data)
    assert auto.brand == "BMW"
    assert auto.model == "sedan"
    assert auto.jahr == 2006
    assert auto.preis_pro_stunde == 35
    assert auto.status is True


def test_invalid_auto_schema():
    data = {
        "brand": "BMW",
        "model": "sedan",
        "jahr": "not_a_number",  # Invalid type
        "preis_pro_stunde": 35,
        "status": True
    }
    with pytest.raises(ValidationError):
        AutoBase(**data)


def test_missing_field_auto_schema():
    data = {
        "brand": "BMW",
        "model": "X5",
        "preis_pro_stunde": 40,
        "status": True
        # Missing 'jahr'
    }
    with pytest.raises(ValidationError):
        AutoBase(**data)


# ------------------------------
# Tests for kundeBase schema
# ------------------------------

def test_valid_kunde_schema():
    data = {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": date(2000, 8, 25),
        "handy_nummer": "0947698022",
        "email": "titor9424@gmail.com"
    }
    kunde = KundenBase(**data)
    assert kunde.vorname == "Tihan"
    assert kunde.nachname == "Ibrahim"
    assert kunde.geb_datum == date(2000, 8, 25)
    assert kunde.handy_nummer == "0947698022"
    assert kunde.email == "titor9424@gmail.com"


def test_invalid_kunde_schema():
    data = {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": date(2000, 8, 25),
        "handy_nummer": "0947698022",
        "email": "invalid_email"  # Invalid format
    }
    with pytest.raises(ValidationError):
        KundenBase(**data)


def test_missing_field_kunde_schema():
    data = {
        "vorname": "Tihan",
        "nachname": "Ali",
        "geb_datum": date(2000, 8, 25),
        # Missing 'handy_nummer' and 'email'
    }
    with pytest.raises(ValidationError):
        KundenBase(**data)


# ------------------------------
# Tests for VertragBase schema
# ------------------------------ 

def test_valid_vertrag():
    data={
        "auto_id": 32 ,
        "kunden_id": 22 ,
        "beginnt_datum": date(2000,4,20),
        "beendet_datum": date(2000,5,25),
        "total_prise": 321.2 ,
        "status" : True
    }

    vertrag=VertragBase(**data)
    assert vertrag.auto_id   ==  32
    assert vertrag.kunden_id ==  22
    assert vertrag.beginnt_datum == date(2000,4,20)
    assert vertrag.beendet_datum == date(2000,5,25)
    assert vertrag.total_prise == 321.2
    assert vertrag.status is True


def test_invalid_vertrag_schema():
    data={
        "auto_id": 32 ,
        "kunden_id": "not a nummer" ,
        "beginnt_datum": date(2000,4,20),
        "beendet_datum": date(2000,5,25),
        "total_prise": 321.2 ,
        "status" : True
    }

    with pytest.raises(ValidationError):
        VertragBase(**data)


def test_massing_field_vertrag_schema():
    data={
        "auto_id": 32 ,
        "kunden_id": "not a nummer" ,
        
        "beendet_datum": date(2000,5,25),
        "total_prise": 321.2 ,
        "status" : True
    }

    with pytest.raises(ValidationError):
        VertragBase(**data)






