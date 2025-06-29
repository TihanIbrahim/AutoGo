import pytest
import secrets
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role  

client = TestClient(app)

# ---------- Hilfsfunktionen ----------

def get_kunden_template():
    """Gibt ein zufälliges, gültiges Kundendaten-Dictionary zurück."""
    random_num = secrets.randbelow(100000) + 1
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random_num}@gmail.com"
    }

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Setzt nach jedem Test automatisch Dependency-Overrides zurück."""
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_kunde():
    """Erstellt vor dem Test einen Kunden mit Rolle 'owner' und gibt ihn zurück."""
    set_user_role("owner")
    data = get_kunden_template()
    response = client.post("/api/v1/dashboard/kunden", json=data)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

# --- Kunden erstellen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 201),   # Owner dürfen Kunden erstellen
    ("viewer", 403),  # Viewer dürfen nicht erstellen
    ("editor", 403),  # Editor dürfen nicht erstellen
])
def test_create_kunden_permissions(role, expected_status):
    """Überprüft, welche Rollen Kunden erstellen dürfen."""
    set_user_role(role)
    response = client.post("/api/v1/dashboard/kunden", json=get_kunden_template())
    assert response.status_code == expected_status

# --- Alle Kunden anzeigen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen alle Kunden sehen
    ("viewer", 200),  # Viewer dürfen alle Kunden sehen
    ("editor", 403),  # Editor dürfen nicht alle Kunden sehen
])
def test_view_all_kunden_permissions(role, expected_status):
    """Testet Zugriffsrechte zum Abrufen aller Kunden."""
    set_user_role(role)
    response = client.get("/api/v1/dashboard/kunden")
    assert response.status_code == expected_status

# --- Kunde nach ID anzeigen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen Kunden einzeln sehen
    ("editor", 403),  # Editor dürfen das nicht
    ("viewer", 403),  # Viewer dürfen das nicht
])
def test_view_kunde_by_id_permissions(role, expected_status, created_kunde):
    """Testet Zugriffsrechte zum Abrufen eines Kunden nach ID."""
    set_user_role(role)
    kunde_id = created_kunde["id"]
    response = client.get(f"/api/v1/dashboard/kunden/{kunde_id}")
    assert response.status_code == expected_status

# --- Kunde aktualisieren ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen Kunden aktualisieren
    ("editor", 200),  # Editor dürfen Kunden aktualisieren
    ("viewer", 403),  # Viewer dürfen das nicht
])
def test_update_kunde_permissions(role, expected_status, created_kunde):
    """Testet Zugriffsrechte zum Aktualisieren von Kundendaten."""
    set_user_role(role)
    kunde_id = created_kunde["id"]
    update_data = {"vorname": "Updated", "handy_nummer": "987654321"}
    response = client.put(f"/api/v1/dashboard/kunden/{kunde_id}", json=update_data)
    assert response.status_code == expected_status

# --- Kunde löschen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 204),   # Owner dürfen Kunden löschen
    ("editor", 403),  # Editor dürfen das nicht
    ("viewer", 403),  # Viewer dürfen das nicht
])
def test_delete_kunde_permissions(role, expected_status, created_kunde):
    """Testet Zugriffsrechte zum Löschen eines Kunden."""
    set_user_role(role)
    kunde_id = created_kunde["id"]
    response = client.delete(f"/api/v1/dashboard/kunden/{kunde_id}")
    assert response.status_code == expected_status

    # Wenn Löschung erlaubt war, prüfen, dass Kunde nicht mehr existiert
    if expected_status == 204:
        get_response = client.get(f"/api/v1/dashboard/kunden/{kunde_id}")
        assert get_response.status_code == 404

# --- Fehlerfall: Nicht vorhandenen Kunden abrufen ---
def test_get_kunde_not_found():
    """Testet Antwort beim Abrufen eines nicht existierenden Kunden."""
    set_user_role("owner")
    response = client.get("/api/v1/dashboard/kunden/999999")
    assert response.status_code == 404

# --- Fehlerfall: Nicht vorhandenen Kunden aktualisieren ---
def test_update_kunde_not_found():
    """Testet Antwort beim Aktualisieren eines nicht existierenden Kunden."""
    set_user_role("owner")
    update_data = {"vorname": "Ghost"}
    response = client.put("/api/v1/dashboard/kunden/999999", json=update_data)
    assert response.status_code == 404

# --- Fehlerfall: Nicht vorhandenen Kunden löschen ---
def test_delete_kunde_not_found():
    """Testet Antwort beim Löschen eines nicht existierenden Kunden."""
    set_user_role("owner")
    response = client.delete("/api/v1/dashboard/kunden/999999")
    assert response.status_code == 404

# --- Ungültige Eingabe: Falsches Email-Format ---
def test_create_kunde_invalid_email():
    """Testet das Erstellen eines Kunden mit ungültiger E-Mail-Adresse."""
    set_user_role("owner")
    data = get_kunden_template()
    data["email"] = "not-an-email"  # Ungültiges Format
    response = client.post("/api/v1/dashboard/kunden", json=data)
    assert response.status_code == 422  # Validierungsfehler von FastAPI
