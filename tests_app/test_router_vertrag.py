import pytest
import random
from datetime import date
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role
import secrets


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
    random_num = secrets.randbelow(100000) + 1
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random_num}@gmail.com"
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

# Clear dependency overrides after each test to avoid side effects
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# Fixture to create a car (Auto) before tests
@pytest.fixture
def created_auto():
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=get_auto_template())
    assert response.status_code == 201
    return response.json()

# Fixture to create a customer (Kunde) before tests
@pytest.fixture
def created_kunde():
    set_user_role("customer")
    response = client.post("/api/v1/kunden", json=get_kunden_template())
    assert response.status_code == 201
    return response.json()

# Fixture to create a contract (Vertrag) before tests
@pytest.fixture
def created_vertrag(created_auto, created_kunde):
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

# --- Test create Vertrag permissions ---
@pytest.mark.parametrize("role, expected_status", [
    ("customer", 201),
    ("guest", 201),
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
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == expected_status

# --- Test cancel Vertrag before start date (should succeed) ---
@pytest.mark.parametrize("role, expected_status", [
    ("customer", 200),
    ("guest", 200),
])
def test_vertrag_kundigen_before_start(role, expected_status, created_auto, created_kunde):
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
    assert resp_cancel.json().get("message") == "Contract was cancelled successfully."


# --- Test cancel Vertrag after start date (should fail) ---
@pytest.mark.parametrize("role, expected_status", [
    ("customer", 400),
    ("guest", 400),
])
def test_vertrag_kundigen_after_start(role, expected_status, created_auto, created_kunde):
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
    assert resp_cancel.json().get("detail") == "Cancellation after contract start is not allowed."


# --- Test create Vertrag with invalid dates (start after end) ---
def test_create_vertrag_invalid_dates(created_auto, created_kunde):
    set_user_role("customer")
    vertrag = get_vertrag_template(
        created_auto["id"],
        created_kunde["id"],
        date(2025, 12, 10),
        date(2025, 12, 1),  # End date before start date
        preis=100.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 400
    assert response.json()["detail"] == "Start date must be before end date."

# --- Test create Vertrag with invalid auto_id ---
def test_create_vertrag_invalid_auto_id(created_kunde):
    set_user_role("customer")
    vertrag = get_vertrag_template(
        999999,  # Non-existent car ID
        created_kunde["id"],
        date(2025, 12, 1),
        date(2025, 12, 10),
        preis=100.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 404
    assert response.json()["detail"] == "Car not found."

# --- Test create Vertrag with invalid kunden_id ---
def test_create_vertrag_invalid_kunden_id(created_auto):
    set_user_role("customer")
    vertrag = get_vertrag_template(
        created_auto["id"],
        999999,  # Non-existent customer ID
        date(2025, 12, 1),
        date(2025, 12, 10),
        preis=100.0
    )
    response = client.post("/api/v1/vertraege", json=vertrag)
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."
