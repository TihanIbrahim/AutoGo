import pytest
import random
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role  
import secrets

client = TestClient(app)

# ---------- Helpers ----------

def get_kunden_template():
    """Returns a random valid customer data dictionary."""
    random_num= secrets.randbelow(100000)+1
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email" :f"user{random_num}@gmail.com"
    }

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Automatically clears dependency overrides after each test."""
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_kunde():
    """Creates a new customer for testing and returns the created object."""
    set_user_role("owner")
    data = get_kunden_template()
    response = client.post("/api/v1/dashboard/kunden", json=data)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

# --- Create Kunden ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 201),
    ("viewer", 403),
    ("editor", 403),
])
def test_create_kunden_permissions(role, expected_status):
    """Test that different user roles can create customers with expected HTTP status codes."""
    set_user_role(role)
    response = client.post("/api/v1/dashboard/kunden", json=get_kunden_template())
    assert response.status_code == expected_status

# --- Show All Kunden ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("viewer", 200),
    ("editor", 403),
])
def test_view_all_kunden_permissions(role, expected_status):
    """Test which roles are allowed to view all customers."""
    set_user_role(role)
    response = client.get("/api/v1/dashboard/kunden")
    assert response.status_code == expected_status

# --- Get Kunde by ID ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("editor", 403),
    ("viewer", 403),
])
def test_view_kunde_by_id_permissions(role, expected_status, created_kunde):
    """Test which roles are allowed to view a customer by ID."""
    set_user_role(role)
    kunde_id = created_kunde["id"]
    response = client.get(f"/api/v1/dashboard/kunden/{kunde_id}")
    assert response.status_code == expected_status

# --- Update Kunde ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),
    ("editor", 200),
    ("viewer", 403),
])
def test_update_kunde_permissions(role, expected_status, created_kunde):
    """Test which roles are allowed to update customer data."""
    set_user_role(role)
    kunde_id = created_kunde["id"]
    update_data = {"vorname": "Updated", "handy_nummer": "987654321"}
    response = client.put(f"/api/v1/dashboard/kunden/{kunde_id}", json=update_data)
    assert response.status_code == expected_status

# --- Delete Kunde ---
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 204),
    ("editor", 403),
    ("viewer", 403),
])
def test_delete_kunde_permissions(role, expected_status, created_kunde):
    """Test which roles are allowed to delete a customer."""
    set_user_role(role)
    kunde_id = created_kunde["id"]
    response = client.delete(f"/api/v1/dashboard/kunden/{kunde_id}")
    assert response.status_code == expected_status

    # If deletion is allowed, confirm the customer is actually deleted
    if expected_status == 204:
        get_response = client.get(f"/api/v1/dashboard/kunden/{kunde_id}")
        assert get_response.status_code == 404

# --- Not Found Case: Get Non-existent Customer ---
def test_get_kunde_not_found():
    """Test response when accessing a non-existent customer."""
    set_user_role("owner")
    response = client.get("/api/v1/dashboard/kunden/999999")
    assert response.status_code == 404

# --- Not Found Case: Update Non-existent Customer ---
def test_update_kunde_not_found():
    """Test response when updating a non-existent customer."""
    set_user_role("owner")
    update_data = {"vorname": "Ghost"}
    response = client.put("/api/v1/dashboard/kunden/999999", json=update_data)
    assert response.status_code == 404

# --- Not Found Case: Delete Non-existent Customer ---
def test_delete_kunde_not_found():
    """Test response when deleting a non-existent customer."""
    set_user_role("owner")
    response = client.delete("/api/v1/dashboard/kunden/999999")
    assert response.status_code == 404

# --- Invalid Input: Invalid Email Format ---
def test_create_kunde_invalid_email():
    """Test creating a customer with an invalid email address."""
    set_user_role("owner")
    data = get_kunden_template()
    data["email"] = "not-an-email"  # Invalid format
    response = client.post("/api/v1/dashboard/kunden", json=data)
    assert response.status_code == 422  # FastAPI will return 422 for validation errors
