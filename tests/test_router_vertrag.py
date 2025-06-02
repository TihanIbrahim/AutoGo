import pytest
from fastapi.testclient import TestClient
from datetime import date
from main import app
from services.dependencies import get_current_user
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
    # Create car (auto) data
    auto = {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": True
    }

    # Create customer (kunde) data with a random email to avoid duplicates
    kunde = {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1, 100000)}@gmail.com"
    }

    # Post car as owner
    set_user_role("owner")
    response_auto = client.post("/api/v1/auto", json=auto)

    # Post customer as customer
    set_user_role("customer")
    response_kunde = client.post("/api/v1/kunde", json=kunde)

    # Ensure both were created successfully
    assert response_auto.status_code == 201
    assert response_kunde.status_code == 201

    return response_auto.json()["id"], response_kunde.json()["id"]

# ===== Test contract creation =====
def test_create_vertrag(create_auto_kunde):
    set_user_role("customer")
    auto_id, kunden_id = create_auto_kunde

    # Create contract data
    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 8, 17)),
        "beendet_datum": str(date(2025, 9, 17)),
        "total_preis": 274.6,
        "status": True
    }

    # Send contract creation request
    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 201

    # Verify returned contract data
    data = response.json()
    assert data["auto_id"] == auto_id
    assert data["kunden_id"] == kunden_id
    assert data["beginnt_datum"] == "2025-08-17"
    assert data["beendet_datum"] == "2025-09-17"
    assert data["total_preis"] == 274.6
    assert data["status"] is True

# ===== Test contract cancellation before the start date =====
def test_vertrag_kundigen(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 9, 27)),
        "beendet_datum": str(date(2025, 10, 27)),
        "total_preis": 244.6,
        "status": True
    }

    set_user_role("customer")
    # Create the contract
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    # Cancel the contract before start date
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
        "beginnt_datum": str(date(2025, 5, 1)),  # Start date in the past
        "beendet_datum": str(date(2025, 5, 27)),
        "total_preis": 244.6,
        "status": True
    }

    # Create the contract
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    # Attempt to cancel after contract has started
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
        "status": True
    }

    set_user_role("customer")
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    # Update contract fields
    update_data = {
        "total_preis": 350.0,
        "status": False
    }

    set_user_role("owner")
    response_update = client.put(f"/api/v1/vertraege/{vertrag_id}", json=update_data)
    assert response_update.status_code == 200

    updated_vertrag = response_update.json()
    assert updated_vertrag["total_preis"] == 350.0
    assert updated_vertrag["status"] is False

# ===== Test retrieving all contracts =====
def test_get_all_vertraege(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 11, 1)),
        "beendet_datum": str(date(2025, 11, 30)),
        "total_preis": 302.0,
        "status": True
    }

    set_user_role("customer")
    # Create a contract
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201

    set_user_role("owner")
    # Retrieve all contracts
    response_get_vertraege = client.get("/api/v1/vertraege")
    assert response_get_vertraege.status_code == 200

    data = response_get_vertraege.json()
    assert isinstance(data, list)
    # Confirm the created contract exists in the list
    assert 302.0 in [v["total_preis"] for v in data]
