import pytest
from fastapi.testclient import TestClient
from main import app
import random
from tests_app.helpers import set_user_role
import secrets


client = TestClient(app)

# ========== Fixtures für wiederverwendbare Eingabedaten ==========

@pytest.fixture
def auto_template():
    # Beispiel-Daten für ein Auto
    return {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2010,
        "preis_pro_stunde": 30,
        "status": "verfügbar"
    }

@pytest.fixture
def generate_kunden_data():
    # Beispiel-Daten für einen Kunden mit zufälliger E-Mail zur Vermeidung von Konflikten
    random_num = secrets.randbelow(100000) + 1
    return {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": "2000-08-25",
        "handy_nummer": "0995719489",
        "email": f"user{random_num}@gmail.com"
    }

@pytest.fixture
def zahlung_template():
    # Beispiel-Daten für eine Zahlung
    return {
        "zahlungsmethode": "karte",
        "datum": "2025-06-01",
        "status": "offen",
        "betrag": 300.0
    }

# ========== Fixtures zur Erstellung von Ressourcen via API ==========

@pytest.fixture
def auto_id(auto_template):
    # Erstellt ein Auto mit der Rolle "owner" und gibt die Auto-ID zurück
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def kunde_id(generate_kunden_data):
    # Erstellt einen Kunden mit der Rolle "customer" und gibt die Kunden-ID zurück
    set_user_role("customer")
    response = client.post("/api/v1/kunden", json=generate_kunden_data)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def vertrag_id(auto_id, kunde_id):
    # Erstellt einen Vertrag zwischen Auto und Kunde und gibt die Vertrags-ID zurück
    contract = {
        "auto_id": auto_id,
        "kunden_id": kunde_id,
        "beginnt_datum": "2025-06-01",
        "beendet_datum": "2025-06-05",
        "status": "aktiv",
        "total_preis": 120.0
    }
    set_user_role("customer")
    response = client.post("/api/v1/vertraege", json=contract)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture(autouse=True)
def clear_overrides():
    # Setzt nach jedem Test die FastAPI-Dependency-Overrides zurück
    yield
    app.dependency_overrides = {}

# ========== Parametrisierte Tests ==========

@pytest.mark.parametrize("role, expected_status", [
    ("customer", 201),
    ("guest", 201),
])
def test_create_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    # Testet, ob verschiedene Benutzerrollen Zahlungen erstellen dürfen
    set_user_role(role)
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/zahlungen", json=zahlung_data)
    assert response.status_code == expected_status
