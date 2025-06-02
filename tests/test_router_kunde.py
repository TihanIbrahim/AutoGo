import pytest
import random
from fastapi.testclient import TestClient
from main import app
from services.dependencies import get_current_user
from tests.helpers import set_user_role  # Utility function to mock user roles (e.g., 'customer', 'owner', 'guest')

client = TestClient(app)

# Returns a template customer dictionary with a random email to avoid duplicates
def get_kunden_template():
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1,100000)}@gmail.com"
    }

# Automatically clear any dependency overrides after each test
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# ======= Tests for creating customers =======

# Test that a customer can successfully create their own profile
def test_create_kunden_with_customer():
    set_user_role("customer")
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["vorname"] == "Test"
    assert res_data["email"] == data["email"]

# Test that an owner is forbidden from creating a customer
def test_create_kunden_with_owner_forbidden():
    set_user_role("owner")
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 403

# Test that a guest is forbidden from creating a customer
def test_create_kunden_with_guest_forbidden():
    set_user_role("guest")
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 403

# ======= Tests for fetching all customers =======

# Test that an owner can view all customers
def test_show_all_kunden_with_owner():
    set_user_role("owner")
    response = client.get("/api/v1/kunden")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Test that a guest is forbidden from viewing all customers
def test_show_all_kunden_with_guest_forbidden():
    set_user_role("guest")
    response = client.get("/api/v1/kunden")
    assert response.status_code == 403

# ======= Tests for fetching a customer by ID =======

# Test that an owner can fetch a specific customer by ID
def test_show_kunde_by_id_with_owner():
    set_user_role("customer")
    data = get_kunden_template()
    create_resp = client.post("/api/v1/kunde", json=data)
    kunde_id = create_resp.json()["id"]

    set_user_role("owner")
    response = client.get(f"/api/v1/kunden/{kunde_id}")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["id"] == kunde_id
    assert res_data["vorname"] == "Test"

# Test that a guest is forbidden from accessing a customer by ID
def test_show_kunde_by_id_with_guest_forbidden():
    set_user_role("guest")
    response = client.get("/api/v1/kunden/1")
    assert response.status_code == 403

# ======= Tests for updating a customer =======

# Test that an owner can update customer information
def test_update_kunde_with_owner():
    set_user_role("customer")
    data = get_kunden_template()
    create_resp = client.post("/api/v1/kunde", json=data)
    kunde_id = create_resp.json()["id"]

    update_data = {
        "vorname": "Mohamed",
        "handy_nummer": "987654321"
    }
    set_user_role("owner")
    response = client.put(f"/api/v1/kunden/{kunde_id}", json=update_data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["vorname"] == "Mohamed"
    assert res_data["handy_nummer"] == "987654321"

# Test that a customer is forbidden from updating data
def test_update_kunde_with_customer_forbidden():
    set_user_role("customer")
    update_data = {"vorname": "Mohamed"}
    response = client.put("/api/v1/kunden/1", json=update_data)
    assert response.status_code == 403

# Test that a guest is forbidden from updating data
def test_update_kunde_with_guest_forbidden():
    set_user_role("guest")
    update_data = {"vorname": "Mohamed"}
    response = client.put("/api/v1/kunden/1", json=update_data)
    assert response.status_code == 403

# ======= Tests for deleting a customer =======

# Test that an owner can delete a customer
def test_delete_kunde_with_owner():
    set_user_role("customer")
    data = get_kunden_template()
    create_resp = client.post("/api/v1/kunde", json=data)
    kunde_id = create_resp.json()["id"]

    set_user_role("owner")
    response = client.delete(f"/api/v1/kunden/{kunde_id}")
    assert response.status_code == 204

# Test that a customer is forbidden from deleting
def test_delete_kunde_with_customer_forbidden():
    set_user_role("customer")
    response = client.delete("/api/v1/kunden/1")
    assert response.status_code == 403

# Test that a guest is forbidden from deleting
def test_delete_kunde_with_guest_forbidden():
    set_user_role("guest")
    response = client.delete("/api/v1/kunden/1")
    assert response.status_code == 403
