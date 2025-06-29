import pytest
import secrets
from datetime import date
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role

client = TestClient(app)

# ---------- Hilfsfunktionen ----------

def get_auto_template():
    """Gibt eine Vorlage für ein gültiges Auto zurück."""
    return {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": "verfügbar"
    }

def get_kunden_template():
    """Erstellt eine zufällige Kundenvorlage mit eindeutiger Email."""
    random_num = secrets.randbelow(100000) + 1
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random_num}@gmail.com"
    }

def get_vertrag_template(auto_id, kunden_id, beginnt, beendet, preis=100.0, status="aktiv"):
    """Erstellt eine Vorlage für einen Vertrag mit den übergebenen Parametern."""
    return {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(beginnt),
        "beendet_datum": str(beendet),
        "total_preis": preis,
        "status": status
    }

def create_vertrag_helper(auto_id, kunden_id, beginnt, beendet, preis=300.0):
    """Hilfsfunktion, um einen Vertrag zu erstellen und dessen JSON zurückzugeben."""
    vertrag = get_vertrag_template(auto_id, kunden_id, beginnt, beendet, preis)
    resp = client.post("/api/v1/dashboard/vertraege", json=vertrag)
    assert resp.status_code == 201
    return resp.json()

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Setzt nach jedem Test automatisch die Dependency-Overrides zurück."""
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_auto():
    """Erstellt ein Auto mit Rolle 'owner' vor dem Test und gibt das Objekt zurück."""
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=get_auto_template())
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_kunde():
    """Erstellt einen Kunden mit Rolle 'owner' vor dem Test und gibt das Objekt zurück."""
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/kunden", json=get_kunden_template())
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_vertrag(created_auto, created_kunde):
    """Erstellt vor dem Test einen Vertrag mit Rolle 'owner' und gibt das Objekt zurück."""
    set_user_role("owner")
    return create_vertrag_helper(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 8, 1),
        date(2025, 8, 31),
        preis=200.0
    )

# ---------- Tests ----------

# --- Vertrag erstellen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 201),   # Owner dürfen Verträge erstellen
    ("editor", 403),  # Editor dürfen nicht erstellen
    ("viewer", 403),  # Viewer dürfen nicht erstellen
])
def test_create_vertrag_permissions(role, expected_status, created_auto, created_kunde):
    """Testet, ob unterschiedliche Rollen Verträge erstellen dürfen."""
    set_user_role(role)
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 9, 1),
        date(2025, 9, 30),
        preis=150.0
    )
    response = client.post("/api/v1/dashboard/vertraege", json=vertrag)
    assert response.status_code == expected_status

# --- Vertrag aktualisieren ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen Verträge aktualisieren
    ("editor", 200),  # Editor dürfen Verträge aktualisieren
    ("viewer", 403),  # Viewer dürfen nicht aktualisieren
])
def test_update_vertrag_permissions(role, expected_status, created_vertrag):
    """Testet Zugriffsrechte zum Aktualisieren eines Vertrags."""
    set_user_role(role)
    update_data = {
        "total_preis": 350.0,
        "status": "beendet"
    }
    vertrag_id = created_vertrag["id"]
    response = client.put(f"/api/v1/dashboard/vertraege/{vertrag_id}", json=update_data)
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data["total_preis"] == 350.0
        assert data["status"] == "beendet"

# --- Alle Verträge abrufen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen alle Verträge sehen
    ("viewer", 200),  # Viewer dürfen alle Verträge sehen
    ("editor", 403),  # Editor dürfen das nicht
])
def test_get_all_vertraege_permissions(role, expected_status):
    """Testet Zugriffsrechte zum Abrufen aller Verträge."""
    set_user_role(role)
    response = client.get("/api/v1/dashboard/vertraege")
    assert response.status_code == expected_status

# --- Vertrag vor Beginn kündigen ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner dürfen Vertrag vor Beginn kündigen
    ("viewer", 403),  # Viewer dürfen nicht kündigen
    ("editor", 403),  # Editor dürfen nicht kündigen
])
def test_vertrag_kundigen_before_start(role, expected_status, created_auto, created_kunde):
    """Testet Kündigung eines Vertrags vor Vertragsbeginn."""
    # Vertrag mit zukünftigem Beginn erstellen
    set_user_role("owner")
    vertrag_created = create_vertrag_helper(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 12, 1),
        date(2025, 12, 31),
        preis=300.0
    )
    vertrag_id = vertrag_created["id"]

    # Kündigungsversuch mit gegebener Rolle
    set_user_role(role)
    resp_cancel = client.post(f"/api/v1/dashboard/vertraege/{vertrag_id}/kuendigen")

    assert resp_cancel.status_code == expected_status
    if expected_status == 200:
        assert resp_cancel.json().get("message") == "Vertrag wurde erfolgreich gekündigt."

# --- Vertrag nach Beginn kündigen (fehlerhaft) ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 400),   # Owner erhalten Fehler 400, wenn Kündigung nach Vertragsbeginn versucht wird
    ("viewer", 403),  # Viewer dürfen nicht kündigen → 403
    ("editor", 403),  # Editor dürfen nicht kündigen → 403
])
def test_vertrag_kundigen_after_start(role, expected_status, created_auto, created_kunde):
    """Testet Kündigung eines Vertrags nach Vertragsbeginn, was nicht erlaubt ist."""
    # Vertrag mit vergangenem Beginn erstellen
    set_user_role("owner")
    vertrag_created = create_vertrag_helper(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 1, 1),
        date(2025, 1, 31),
        preis=300.0
    )
    vertrag_id = vertrag_created["id"]

    # Kündigungsversuch mit gegebener Rolle
    set_user_role(role)
    resp_cancel = client.post(f"/api/v1/dashboard/vertraege/{vertrag_id}/kuendigen")

    assert resp_cancel.status_code == expected_status
    if expected_status == 400:
        assert resp_cancel.json().get("detail") == "Kündigung nach Vertragsbeginn ist nicht möglich."
