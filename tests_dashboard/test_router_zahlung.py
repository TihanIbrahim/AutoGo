import pytest
from fastapi.testclient import TestClient
from main import app
import random
from tests_app.helpers import set_user_role
import secrets

client = TestClient(app)

# ========== Fixtures for reusable input data ==========

# Sample data for a car
@pytest.fixture
def auto_template():
    return {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2010,
        "preis_pro_stunde": 30,
        "status": "verfügbar"
    }

# Randomized customer data
@pytest.fixture
def generate_kunden_data():
    random_num= secrets.randbelow(100000)+1
    return {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": "2000-08-25",
        "handy_nummer": "0995719489",
        "email" :f"user{random_num}@gmail.com"
    }

# Sample data for a payment
@pytest.fixture
def zahlung_template():
    return {
        "zahlungsmethode": "karte",
        "datum": "2025-06-01",
        "status": "offen",
        "betrag": 300.0
    }

# ========== Fixtures to create actual resources via API ==========

# Create a car and return its ID
@pytest.fixture
def auto_id(auto_template):
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

# Create a customer and return its ID
@pytest.fixture
def kunde_id(generate_kunden_data):
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/kunden", json=generate_kunden_data)
    assert response.status_code == 201
    return response.json()["id"]

# Create a contract and return its ID
@pytest.fixture
def vertrag_id(auto_id, kunde_id):
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

# Clear dependency overrides after each test
@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides = {}

# ========== Parametrized Tests ==========

# Test which roles are allowed to create a payment
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 201),
    ("editor", 403),
    ("viewer", 403),
])
def test_create_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    set_user_role(role)
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/dashboard/zahlungen", json=zahlung_data)
    assert response.status_code == expected_status

# Test which roles can retrieve all payments
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("editor", 403),
    ("viewer", 200),
])
def test_list_zahlungen_permissions(role, expected_status):
    set_user_role(role)
    response = client.get("/api/v1/dashboard/zahlungen")
    assert response.status_code == expected_status

# Test which roles can update a payment
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("editor", 200),  # editor is assumed to have update rights
    ("viewer", 403)
])
def test_update_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    # First, create a payment
    set_user_role("owner")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/dashboard/zahlungen", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    # Try updating the payment with the specified role
    set_user_role(role)
    zahlung_update = zahlung_template.copy()
    zahlung_update["betrag"] = 999.99
    zahlung_update["vertrag_id"] = vertrag_id

    response = client.put(f"/api/v1/dashboard/zahlungen/{zahlung_id}", json=zahlung_update)
    assert response.status_code == expected_status

    # If update succeeded, verify the change
    if expected_status == 200:
        updated = response.json()
        assert updated["betrag"] == 999.99

# Test which roles can delete a payment
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 204),
    ("editor", 403),
    ("viewer", 403)
])
def test_delete_zahlung_permissions(role, expected_status, vertrag_id, zahlung_template):
    # Create a payment first
    set_user_role("owner")
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertrag_id"] = vertrag_id
    response = client.post("/api/v1/dashboard/zahlungen", json=zahlung_data)
    assert response.status_code == 201
    zahlung_id = response.json()["id"]

    # Try deleting with the given role
    set_user_role(role)
    response = client.delete(f"/api/v1/dashboard/zahlungen/{zahlung_id}")
    assert response.status_code == expected_status


# Optional: Test Not Found cases for update and delete
def test_update_zahlung_not_found():
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
    set_user_role("owner")
    response = client.delete("/api/v1/dashboard/zahlungen/999999")
    assert response.status_code == 404
