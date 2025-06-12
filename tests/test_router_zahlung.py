import pytest
from fastapi.testclient import TestClient
from main import app
import random
from tests.helpers import set_user_role

client = TestClient(app)

# ========== Fixtures for reusable input data ==========

@pytest.fixture
def auto_template():
    # Basic car data
    return {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2010,
        "preis_pro_stunde": 30,
        "status": "verfügbar"
    }

@pytest.fixture
def generate_kunden_data():
    # Basic customer data with random email to avoid conflict
    return {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": "2000-08-25",
        "handy_nummer": "0995719489",
        "email": f"titor{random.randint(1, 1000000)}@gmail.com"
    }

@pytest.fixture
def zahlung_template():
    # Payment data template
    return {
        "zahlungsmethode":"karte",
        "datum": "2025-06-01",
        "status": "offen",
        "betrag": 300.0
    }

# ========== Fixtures to create actual resources via API ==========

@pytest.fixture
def auto_id(auto_template):
    # Create car as owner
    set_user_role("owner")
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def kunde_id(generate_kunden_data):
    # Create customer as customer
    set_user_role("customer")
    response = client.post("/api/v1/kunde", json=generate_kunden_data)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def vertrag_id(auto_id, kunde_id):
    # Create contract between car and customer
    contract = {
        "auto_id": auto_id,
        "kunden_id": kunde_id,
        "beginnt_datum": "2025-06-01",
        "beendet_datum": "2025-06-05",
        "status": "aktiv",
        "total_preis": 120.0
    }
    set_user_role("customer")
    response = client.post("/api/v1/vertrag", json=contract)
    assert response.status_code == 201
    return response.json()["id"]

# ========== Automatically clear dependency overrides ==========

@pytest.fixture(autouse=True)
def clear_overrides():
    # Reset role override after each test
    yield
    app.dependency_overrides = {}

# ========== Payment Endpoint Tests ==========

def test_create_zahlung_with_customer(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Customers can create payments
    set_user_role("customer")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id

    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 201

    data = response.json()
    assert data["vertrag_id"] == vertrag_id
    assert data["zahlungsmethode"] == zahlung_data["zahlungsmethode"]
    assert data["betrag"] == zahlung_data["betrag"]

def test_create_zahlung_with_owner(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Owners should NOT be allowed to create payments
    set_user_role("owner")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id

    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 403  # Should be forbidden

def test_create_zahlung_with_guest(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Guests should NOT be allowed to create payments
    set_user_role("guest")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id

    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 403

def test_list_zahlungen_with_owner():
    # Owners can list all payments
    set_user_role("owner")
    response = client.get("/api/v1/zahlungen")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_zahlungen_with_customer():
    # Customers are not allowed to list all payments
    set_user_role("customer")
    response = client.get("/api/v1/zahlungen")
    assert response.status_code == 403

def test_list_zahlungen_with_guest():
    # Guests are not allowed to list payments
    set_user_role("guest")
    response = client.get("/api/v1/zahlungen")
    assert response.status_code == 403

def test_update_zahlung_with_owner(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Create a payment first
    set_user_role("customer")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    # Update payment as owner 
    set_user_role("owner")   
    zahlung_update = zahlung_template.copy()
    zahlung_update["betrag"] = 350.0
    zahlung_update["vertrag_id"] = vertrag_id

    response = client.put(f"/api/v1/zahlungen/{zahlung_id}", json=zahlung_update)
    assert response.status_code == 200
    updated = response.json()
    assert updated["betrag"] == 350.0
    assert updated["datum"] == zahlung_template["datum"]

def test_update_zahlung_with_customer(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Create and update payment as customer
    set_user_role("customer")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    zahlung_update = zahlung_template.copy()
    zahlung_update["betrag"] = 400.0
    zahlung_update["vertrag_id"] = vertrag_id

    response = client.put(f"/api/v1/zahlungen/{zahlung_id}", json=zahlung_update)
    assert response.status_code == 200
    updated = response.json()
    assert updated["betrag"] == 400.0
    assert updated["datum"] == zahlung_template["datum"]

def test_update_zahlung_with_guest():
    # Guests should NOT be able to update payments
    set_user_role("guest")
    response = client.put("/api/v1/zahlungen/1", json={
        "vertrag_id": 1,
        "zahlungsmethode": "karte",
        "datum": "2025-05-01",
        "status": "bezahlt",
        "betrag": 100.0  
    })
    assert response.status_code == 403

def test_delete_zahlung_with_owner(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Create a payment as customer
    set_user_role("customer")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    # Delete payment as owner
    set_user_role("owner")
    delete_response = client.delete(f"/api/v1/zahlungen/{zahlung_id}")
    assert delete_response.status_code == 204

def test_delete_zahlung_with_customer():
    # Customers should NOT be allowed to delete payments
    set_user_role("customer")
    response = client.delete("/api/v1/zahlungen/1")
    assert response.status_code == 403

def test_delete_zahlung_with_guest():
    # Guests should NOT be allowed to delete payments
    set_user_role("guest")
    response = client.delete("/api/v1/zahlungen/1")
    assert response.status_code == 403
