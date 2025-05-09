from fastapi.testclient import TestClient
from datetime import date
from main import app
import random
import pytest

client = TestClient(app)

@pytest.fixture
def create_auto_kunde():
    auto = {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": True
    }

    kunde = {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1,100000)}@gmail.com"
    }

    response_create_Auto = client.post("/api/v1/auto", json=auto)
    response_create_kunde = client.post("/api/v1/kunde", json=kunde)

    assert response_create_Auto.status_code == 200
    assert response_create_kunde.status_code == 200

    return response_create_Auto.json()["id"], response_create_kunde.json()["id"]

def test_create_vertrag(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 8, 17)),
        "beendet_datum": str(date(2025, 9, 17)),
        "total_prise": 274.6,
        "status": True
    }

    response_vertrag = client.post("/api/v1/vertrag", json=vertrag)
    assert response_vertrag.status_code == 200

    data = response_vertrag.json()
    assert data["auto_id"] == auto_id
    assert data["kunden_id"] == kunden_id
    assert data["beginnt_datum"] == "2025-08-17"
    assert data["beendet_datum"] == "2025-09-17"
    assert data["total_prise"] == 274.6
    assert data["status"] is True

def test_vertrag_kundigen(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 9, 27)),
        "beendet_datum": str(date(2025, 10, 27)),
        "total_prise": 244.6,
        "status": True
    }

    response_vertrag = client.post("/api/v1/vertrag", json=vertrag)
    assert response_vertrag.status_code == 200

    vertrag_id = response_vertrag.json()["id"]

    response_kundigen = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert response_kundigen.status_code == 200
    assert response_kundigen.json().get("message") == "Der Vertrag wurde gekündiget"

def test_vertrag_kundigen_nach_start(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 5, 1)),
        "beendet_datum": str(date(2025, 5, 27)),
        "total_prise": 244.6,
        "status": True
    }

    response_creat_vertrag = client.post("/api/v1/vertrag", json=vertrag)
    assert response_creat_vertrag.status_code == 200
    vertrag_id = response_creat_vertrag.json()["id"]

    response_kundigen_nach_start = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")

    assert response_kundigen_nach_start.status_code == 400
    assert response_kundigen_nach_start.json().get("detail") == "Leider konnten Sie den Vertrag nicht kündigen."
