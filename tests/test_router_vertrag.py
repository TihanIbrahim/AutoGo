import pytest
from fastapi.testclient import TestClient
from datetime import date
from main import app
from models.auto import AutoStatus
import random
from tests.helpers import set_user_role

client = TestClient(app)

# ===== Automatically reset dependency overrides after each test =====
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# ===== Fixture to create both a car and a customer =====
@pytest.fixture
def create_auto_kunde():
    auto = {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": "verfügbar"
    }

    kunde = {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1, 100000)}@gmail.com"
    }

    set_user_role("owner")
    response_auto = client.post("/api/v1/auto", json=auto)

    set_user_role("customer")
    response_kunde = client.post("/api/v1/kunde", json=kunde)

    assert response_auto.status_code == 201
    assert response_kunde.status_code == 201

    return response_auto.json()["id"], response_kunde.json()["id"]

# ===== Test contract creation =====
def test_create_vertrag(create_auto_kunde):
    set_user_role("customer")
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 8, 17)),
        "beendet_datum": str(date(2025, 9, 17)),
        "total_preis": 274.6,
        "status": "aktiv"
    }

    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 201

    data = response.json()
    assert data["auto_id"] == auto_id
    assert data["kunden_id"] == kunden_id
    assert data["beginnt_datum"] == "2025-08-17"
    assert data["beendet_datum"] == "2025-09-17"
    assert data["total_preis"] == 274.6
    assert data["status"] == "aktiv"

# ===== Test contract cancellation before the start date =====
def test_vertrag_kundigen(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 9, 27)),
        "beendet_datum": str(date(2025, 10, 27)),
        "total_preis": 244.6,
        "status": "aktiv"
    }

    set_user_role("customer")
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    response_kundigen = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert response_kundigen.status_code == 200
    assert response_kundigen.json().get("message") == "Vertrag wurde erfolgreich gekündigt."

# ===== Test contract cancellation after the start date should fail =====
def test_vertrag_kundigen_nach_start(create_auto_kunde):
    set_user_role("customer")
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 5, 1)),
        "beendet_datum": str(date(2025, 5, 27)),
        "total_preis": 244.6,
        "status": "aktiv"
    }

    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    response_kundigen = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert response_kundigen.status_code == 400
    assert response_kundigen.json().get("detail") == "Kündigung nach Vertragsbeginn ist nicht möglich."

# ===== Test updating an existing contract =====
def test_update_vertrag(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 10, 1)),
        "beendet_datum": str(date(2025, 10, 30)),
        "total_preis": 300.0,
        "status": "aktiv"
    }

    set_user_role("customer")
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    update_data = {
        "total_preis": 350.0,
        "status": "beendet"
    }

    set_user_role("owner")
    response_update = client.put(f"/api/v1/vertraege/{vertrag_id}", json=update_data)
    assert response_update.status_code == 200

    updated_vertrag = response_update.json()
    assert updated_vertrag["total_preis"] == 350.0
    assert updated_vertrag["status"] == "beendet"

# ===== Test retrieving all contracts =====
def test_get_all_vertraege(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 11, 1)),
        "beendet_datum": str(date(2025, 11, 30)),
        "total_preis": 302.0,
        "status": "aktiv"
    }

    set_user_role("customer")
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201

    set_user_role("owner")
    response_get_vertraege = client.get("/api/v1/vertraege")
    assert response_get_vertraege.status_code == 200

    data = response_get_vertraege.json()
    assert isinstance(data, list)
    assert 302.0 in [v["total_preis"] for v in data]

# ===== Test creating contract with end date before start date =====
def test_create_vertrag_invalid_date_order(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 12, 10)),
        "beendet_datum": str(date(2025, 12, 1)),  # Invalid: end date before start date
        "total_preis": 200.0,
        "status": "aktiv"
    }

    set_user_role("customer")
    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 400
    assert response.json()["detail"] == "Startdatum muss vor dem Enddatum liegen."

# ===== Test creating contract with non-existing auto ID =====
def test_create_vertrag_with_invalid_auto_id(create_auto_kunde):
    _, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": 999999,  # Invalid auto_id
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 12, 1)),
        "beendet_datum": str(date(2025, 12, 10)),
        "total_preis": 100.0,
        "status": "aktiv"
    }

    set_user_role("customer")
    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 404
    assert response.json()["detail"] == "Auto nicht gefunden."

# ===== Test creating contract with non-existing customer ID =====
def test_create_vertrag_with_invalid_kunden_id(create_auto_kunde):
    auto_id, _ = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": 999999,  # Invalid kunden_id
        "beginnt_datum": str(date(2025, 12, 1)),
        "beendet_datum": str(date(2025, 12, 10)),
        "total_preis": 100.0,
        "status": "aktiv"
    }

    set_user_role("customer")
    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 404
    assert response.json()["detail"] == "Kunde nicht gefunden."
