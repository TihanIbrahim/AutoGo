import pytest
import random
from fastapi.testclient import TestClient
from main import app
from tests.helpers import set_user_role  # Utility function to mock user roles (e.g., 'customer', 'owner', 'guest')

client = TestClient(app)

# ---------- Helpers ----------

def get_kunden_template():
    # Returns a sample customer data with a unique email to avoid duplicates
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1,100000)}@gmail.com"
    }

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    # Clear any dependency overrides after each test automatically
    yield
    app.dependency_overrides = {}

# Fixture: Create a customer and return its data for reuse in tests
@pytest.fixture
def created_kunde():
    set_user_role("customer")
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

# --- Create Kunden ---
def test_create_kunden_with_customer():
    # Test that a customer can successfully create their own profile
    set_user_role("customer")
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["vorname"] == "Test"
    assert res_data["email"] == data["email"]

def test_create_kunden_with_owner_forbidden():
    # Test that an owner is forbidden from creating a customer
    set_user_role("owner")
    response = client.post("/api/v1/kunde", json=get_kunden_template())
    assert response.status_code == 403

def test_create_kunden_with_guest_forbidden():
    # Test that a guest is forbidden from creating a customer
    set_user_role("guest")
    response = client.post("/api/v1/kunde", json=get_kunden_template())
    assert response.status_code == 403

# --- Show All Kunden ---
def test_show_all_kunden_with_owner():
    # Test that an owner can view all customers
    set_user_role("owner")
    response = client.get("/api/v1/kunden")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_show_all_kunden_with_guest_forbidden():
    # Test that a guest is forbidden from viewing all customers
    set_user_role("guest")
    response = client.get("/api/v1/kunden")
    assert response.status_code == 403

# --- Get Kunden by ID ---
def test_show_kunde_by_id_with_owner(created_kunde):
    # Test that an owner can fetch a specific customer by ID
    kunde_id = created_kunde["id"]
    set_user_role("owner")
    response = client.get(f"/api/v1/kunden/{kunde_id}")
    assert response.status_code == 200
    assert response.json()["id"] == kunde_id

def test_show_kunde_by_id_with_guest_forbidden():
    # Test that a guest is forbidden from accessing a customer by ID
    set_user_role("guest")
    response = client.get("/api/v1/kunden/1")
    assert response.status_code == 403

def test_get_kunde_not_found():
    # Test that requesting a non-existent customer returns 404
    set_user_role("owner")
    response = client.get("/api/v1/kunden/999999")
    assert response.status_code == 404

# --- Update Kunden ---
def test_update_kunde_with_owner(created_kunde):
    # Test that an owner can update customer information
    kunde_id = created_kunde["id"]
    update_data = {"vorname": "Mohamed", "handy_nummer": "987654321"}
    set_user_role("owner")
    response = client.put(f"/api/v1/kunden/{kunde_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["vorname"] == "Mohamed"

def test_update_kunde_with_customer_forbidden():
    # Test that a customer is forbidden from updating customer data
    set_user_role("customer")
    response = client.put("/api/v1/kunden/1", json={"vorname": "Mohamed"})
    assert response.status_code == 403

def test_update_kunde_with_guest_forbidden():
    # Test that a guest is forbidden from updating customer data
    set_user_role("guest")
    response = client.put("/api/v1/kunden/1", json={"vorname": "Mohamed"})
    assert response.status_code == 403

# --- Delete Kunden ---
def test_delete_kunde_with_owner(created_kunde):
    # Test that an owner can delete a customer
    kunde_id = created_kunde["id"]
    set_user_role("owner")
    response = client.delete(f"/api/v1/kunden/{kunde_id}")
    assert response.status_code == 204

def test_delete_kunde_with_customer_forbidden():
    # Test that a customer is forbidden from deleting a customer
    set_user_role("customer")
    response = client.delete("/api/v1/kunden/1")
    assert response.status_code == 403

def test_delete_kunde_with_guest_forbidden():
    # Test that a guest is forbidden from deleting a customer
    set_user_role("guest")
    response = client.delete("/api/v1/kunden/1")
    assert response.status_code == 403
