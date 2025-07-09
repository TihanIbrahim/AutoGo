import pytest
from fastapi.testclient import TestClient
from main import app
import secrets
from tests_app.helpers import set_user_role

client = TestClient(app)

# ========== Fixtures für wiederverwendbare Eingabedaten ==========

@pytest.fixture
def auto_template():
    """Beispiel-Daten für ein Auto."""
    return {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2010,
        "preis_pro_stunde": 30,
        "status": "verfügbar"
    }

@pytest.fixture
def generate_kunden_data():
    """Erstellt zufällige Kundendaten mit eindeutiger Email."""
    random_num= secrets.randbelow(100000)+1
    return {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": "2000-08-25",
        "handy_nummer": "0995719489",
        "email" :f"user{random_num}@gmail.com"
    }

@pytest.fixture
def zahlung_template():
    """Beispiel-Daten für eine Zahlung."""
    return {
        "zahlungsmethode": "karte",
        "datum": "2025-06-01",
        "status": "offen",
        "betrag": 300.0
    }

# ========== Fixtures zum Erstellen von Ressourcen über die API ==========

@pytest.fixture
def auto_id(auto_template):
    """Erstellt ein Auto und gibt die ID zurück."""
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def kunde_id(generate_kunden_data):
    """Erstellt einen Kunden und gibt die ID zurück."""
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/kunden", json=generate_kunden_data)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def vertrag_id(auto_id, kunde_id):
    """Erstellt einen Vertrag und gibt die ID zurück."""
    contract = {
        "auto_id": auto_id,
        "kunden_id": kunde_id,
        "beginnt_datum": "2025-06-01",
        "beendet_datum": "2025-06-05",
        "status": "aktiv",
        "total_preis": 120.0
    }
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/vertraege", json=contract)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture(autouse=True)
def clear_overrides():
    """Setzt nach jedem Test Dependency-Overrides zurück."""
    yield
    app.dependency_overrides = {}

# ========== Parametrisierte Tests ==========

@pytest.mark.parametrize("role, expected_status", [
    ("owner", 201),   # Owner dürfen Zahlungen anlegen
    ("editor", 403),  # Editor nicht erlaubt
    ("viewer", 403),  # Viewer nicht erlaubt
])
def test_create_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    """Testet, welche Rollen Zahlungen anlegen dürfen."""
    set_user_role(role)
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/dashboard/zahlungen", json=zahlung_data)
    assert response.status_code == expected_status

@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen alle Zahlungen sehen
    ("editor", 403),  # Editor nicht erlaubt
    ("viewer", 200),  # Viewer dürfen alle Zahlungen sehen
])
def test_list_zahlungen_permissions(role, expected_status):
    """Testet, welche Rollen Zahlungen abrufen dürfen."""
    set_user_role(role)
    response = client.get("/api/v1/dashboard/zahlungen")
    assert response.status_code == expected_status

@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen Zahlungen aktualisieren
    ("editor", 200),  # Editor dürfen Zahlungen aktualisieren
    ("viewer", 403),  # Viewer dürfen nicht aktualisieren
])
def test_update_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    """Testet Aktualisierungsrechte für Zahlungen je Rolle."""
    set_user_role("owner")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/dashboard/zahlungen", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    set_user_role(role)
    zahlung_update = zahlung_template.copy()
    zahlung_update["betrag"] = 999.99
    zahlung_update["vertrag_id"] = vertrag_id

    response = client.put(f"/api/v1/dashboard/zahlungen/{zahlung_id}", json=zahlung_update)
    assert response.status_code == expected_status

    if expected_status == 200:
        updated = response.json()
        assert updated["betrag"] == 999.99

@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen Zahlungen löschen
    ("editor", 403),  # Editor nicht erlaubt
    ("viewer", 403),  # Viewer nicht erlaubt
])
def test_delete_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    """Testet Löschrechte für Zahlungen je Rolle."""
    set_user_role("owner")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/dashboard/zahlungen", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    set_user_role(role)
    response = client.delete(f"/api/v1/dashboard/zahlungen/{zahlung_id}")
    assert response.status_code == expected_status

def test_update_zahlung_not_found():
    """Testet Fehler 404 beim Aktualisieren einer nicht existierenden Zahlung."""
    set_user_role("owner")
    response = client.put("/api/v1/dashboard/zahlungen/999999", json={
        "vertrag_id": 1,
        "zahlungsmethode": "karte",
        "datum": "2025-05-01",
        "status": "bezahlt",
        "betrag": 100.0
    })
    assert response.status_code == 404

def test_delete_zahlung_not_found():
    """Testet Fehler 404 beim Löschen einer nicht existierenden Zahlung."""
    set_user_role("owner")
    response = client.delete("/api/v1/dashboard/zahlungen/999999")
    assert response.status_code == 404
