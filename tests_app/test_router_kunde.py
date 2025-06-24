import pytest
import random
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role
import secrets


client = TestClient(app)

# ---------- Helpers ----------

def get_kunden_template():
    # Returns a sample customer payload with randomized email to avoid conflicts
    random_num= secrets.randbelow(100000) + 1 
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random_num}@gmail.com"
    }

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    # Automatically clear FastAPI dependency overrides after each test
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_kunde():
    # Creates a customer with role 'customer' and returns the created object for reuse
    set_user_role("customer")
    data = get_kunden_template()
    response = client.post("/api/v1/kunden", json=data)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

# --- Create Kunden ---
@pytest.mark.parametrize("role, expected_status", [
    ("customer", 201),
    ("guest", 201),
])
def test_create_kunden_permissions(role, expected_status):
    # Test that different user roles can create customers with expected HTTP status codes
    set_user_role(role)
    response = client.post("/api/v1/kunden", json=get_kunden_template())
    assert response.status_code == expected_status
