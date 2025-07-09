import pytest
from datetime import date
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role
import secrets

client = TestClient(app)

# ---------- Hilfsfunktionen ----------

def get_auto_template():
    # Liefert eine Beispiel-Payload für ein Auto zurück
    return {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": "verfügbar"
    }

def get_kunden_template():
    # Liefert eine Beispiel-Payload für einen Kunden zurück
    # E-Mail wird mit Zufallszahl versehen, um Konflikte zu vermeiden
    random_num = secrets.randbelow(100000) + 1
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random_num}@gmail.com"
    }

def get_vertrag_template(auto_id, kunden_id, beginnt, beendet, preis=100.0, status="aktiv"):
    # Liefert eine Beispiel-Payload für einen Vertrag zurück
    return {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(beginnt),
        "beendet_datum": str(beendet),
        "total_preis": preis,
        "status": status
    }

# ---------- Fixtures ----------

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    # Nach jedem Test werden FastAPI-Dependency-Overrides zurückgesetzt
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_auto():
    # Erstellt ein Auto mit der Rolle 'owner' und liefert die Antwort zurück
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=get_auto_template())
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_kunde():
    # Erstellt einen Kunden mit der Rolle 'customer' und liefert die Antwort zurück
    set_user_role("customer")
    response = client.post("/api/v1/kunden", json=get_kunden_template())
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_vertrag(created_auto, created_kunde):
    # Erstellt einen Vertrag zwischen einem Auto und Kunden (beide existieren)
    set_user_role("customer")
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 8, 1),
        date(2025, 8, 31),
        preis=200.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

@pytest.mark.parametrize("role, expected_status", [
    ("customer", 201),
    ("guest", 201),
])
def test_create_vertrag_permissions(role, expected_status, created_auto, created_kunde):
    # Testet, dass verschiedene Rollen Verträge anlegen dürfen
    set_user_role(role)
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 9, 1),
        date(2025, 9, 30),
        preis=150.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == expected_status

@pytest.mark.parametrize("role, expected_status", [
    ("customer", 200),
    ("guest", 200),
])
def test_vertrag_kundigen_before_start(role, expected_status, created_auto, created_kunde):
    # Testet das erfolgreiche Kündigen eines Vertrags VOR Vertragsbeginn
    set_user_role(role)
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 12, 1),
        date(2025, 12, 31),
        preis=300.0
    )
    resp_create = client.post("/api/v1/vertraege", json=vertrag)
    assert resp_create.status_code == 201
    vertrag_id = resp_create.json()["id"]

    resp_cancel = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert resp_cancel.status_code == expected_status
    assert resp_cancel.json().get("message") == "Vertrag wurde erfolgreich gekündigt."

@pytest.mark.parametrize("role, expected_status", [
    ("customer", 400),
    ("guest", 400),
])
def test_vertrag_kundigen_after_start(role, expected_status, created_auto, created_kunde):
    # Testet, dass Kündigung nach Vertragsbeginn nicht erlaubt ist
    set_user_role(role)
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 1, 1),
        date(2025, 1, 31),
        preis=300.0
    )
    resp_create = client.post("/api/v1/vertraege", json=vertrag)
    assert resp_create.status_code == 201
    vertrag_id = resp_create.json()["id"]

    resp_cancel = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert resp_cancel.status_code == expected_status
    assert resp_cancel.json().get("detail") == "Kündigung nach Vertragsbeginn ist nicht erlaubt."

def test_create_vertrag_invalid_dates(created_auto, created_kunde):
    # Testet, dass das Erstellen eines Vertrags mit Enddatum vor Startdatum fehlschlägt
    set_user_role("customer")
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 12, 10),
        date(2025, 12, 1),  # Enddatum vor Startdatum
        preis=100.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 400
    assert response.json()["detail"] == "Startdatum muss vor Enddatum liegen."

def test_create_vertrag_invalid_auto_id(created_kunde):
    # Testet, dass das Erstellen eines Vertrags mit ungültiger Auto-ID 404 zurückgibt
    set_user_role("customer")
    vertrag = get_vertrag_template(
        999999,  # Nicht vorhandene Auto-ID
        created_kunde["id"],
        date(2025, 12, 1),
        date(2025, 12, 10),
        preis=100.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 404
    assert "nicht gefunden" in response.json()["detail"]

def test_create_vertrag_invalid_kunden_id(created_auto):
    # Testet, dass das Erstellen eines Vertrags mit ungültiger Kunden-ID 404 zurückgibt
    set_user_role("customer")
    vertrag = get_vertrag_template(
        created_auto["id"],
        999999,  # Nicht vorhandene Kunden-ID
        date(2025, 12, 1),
        date(2025, 12, 10),
        preis=100.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 404
    assert "Kunde mit ID" in response.json()["detail"] and "nicht gefunden" in response.json()["detail"]
