import pytest
import random
from datetime import date
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role

client = TestClient(app)

# ---------- Helpers ----------

def get_auto_template():
    return {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": "verfügbar"
    }

def get_kunden_template():
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1, 100000)}@gmail.com"
    }

def get_vertrag_template(auto_id, kunden_id, beginnt, beendet, preis=100.0, status="aktiv"):
    return {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(beginnt),
        "beendet_datum": str(beendet),
        "total_preis": preis,
        "status": status
    }

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_auto():
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=get_auto_template())
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_kunde():
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/kunden", json=get_kunden_template())
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_vertrag(created_auto, created_kunde):
    set_user_role("owner")
    vertrag = get_vertrag_template(
        created_auto["id"], 
        created_kunde["id"], 
        date(2025, 8, 1), 
        date(2025, 8, 31), 
        preis=200.0
    )
    response = client.post("/api/v1/dashboard/vertraege", json=vertrag)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

# --- Create Vertrag ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 201),
    ("editor", 403),
    ("viewer", 403),
])
def test_create_vertrag_permissions(role, expected_status, created_auto, created_kunde):
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

# --- Update Vertrag ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("editor", 200),
    ("viewer", 403),
])
def test_update_vertrag_permissions(role, expected_status, created_vertrag):
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

# --- Get all Vertraege ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("viewer", 200),
    ("editor", 403),
])
def test_get_all_vertraege_permissions(role, expected_status):
    set_user_role(role)
    response = client.get("/api/v1/dashboard/vertraege")
    assert response.status_code == expected_status

# --- Cancel contract before start date ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),   # Owner can cancel contract before start date successfully
    ("viewer", 403),  # Viewer is forbidden to cancel contract
    ("editor", 403),  # Editor is forbidden to cancel contract
])
def test_vertrag_kundigen_before_start(role, expected_status, created_auto, created_kunde):
    set_user_role("owner")  

    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 12, 1),
        date(2025, 12, 31),
        preis=300.0
    )

    resp_create = client.post("/api/v1/dashboard/vertraege", json=vertrag)
    assert resp_create.status_code == 201

    vertrag_id = resp_create.json()["id"]

    set_user_role(role)
    resp_cancel = client.post(f"/api/v1/dashboard/vertraege/{vertrag_id}/kuendigen")

    assert resp_cancel.status_code == expected_status
    if expected_status == 200:
        assert resp_cancel.json().get("message") == "Vertrag wurde erfolgreich gekündigt."

# --- Cancel Vertrag after start date (fail) ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 400),   # Owner tries to cancel after contract started → error 400
    ("viewer", 403),  # Viewer forbidden to cancel → 403
    ("editor", 403),  # Editor forbidden to cancel → 403
])
def test_vertrag_kundigen_after_start(role, expected_status, created_auto, created_kunde):
    set_user_role("owner")
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 1, 1),
        date(2025, 1, 31),
        preis=300.0
    )
    resp_create = client.post("/api/v1/dashboard/vertraege", json=vertrag)
    assert resp_create.status_code == 201
    vertrag_id = resp_create.json()["id"]

    set_user_role(role)
    resp_cancel = client.post(f"/api/v1/dashboard/vertraege/{vertrag_id}/kuendigen")
    assert resp_cancel.status_code == expected_status
    if expected_status == 400:
        assert resp_cancel.json().get("detail") == "Kündigung nach Vertragsbeginn ist nicht möglich."
