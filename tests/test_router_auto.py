import pytest
from fastapi.testclient import TestClient
from main import app
from services.dependencies import get_current_user
from tests.helpers import set_user_role  # Helper function to set user role for tests

client = TestClient(app)

# Sample car data to use in create car tests
auto_template = {
    "brand": "BMW",
    "model": "sedan",
    "jahr": 2010,
    "preis_pro_stunde": 30,
    "status": True
}

# Pytest fixture that automatically clears dependency overrides after each test
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# ======= Permission and functionality tests =======

# Test creating a car as a user with 'owner' role (should succeed)
def test_create_auto_with_owner():
    set_user_role("owner")  # Set current user role to 'owner'
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 201  # Check creation was successful (HTTP 201)
    data = response.json()
    assert data["brand"] == "BMW"
    assert data["preis_pro_stunde"] == 30

# Test creating a car as a user with 'customer' role (should be forbidden)
def test_create_auto_with_customer():
    set_user_role("customer")
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 403  # Access forbidden

# Test creating a car as a user with 'guest' role (should be forbidden)
def test_create_auto_with_guest():
    set_user_role("guest")
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 403  # Access forbidden

# Test fetching all cars as 'owner' (should succeed)
def test_show_all_auto_with_owner():
    set_user_role("owner")
    response = client.get("/api/v1/autos")
    assert response.status_code == 200  # OK response
    autos = response.json()
    assert isinstance(autos, list)  # Should return a list of cars
    assert len(autos) > 0  # There should be at least one car

# Test fetching all cars as 'guest' (should be forbidden)
def test_show_all_auto_with_guest():
    set_user_role("guest")
    response = client.get("/api/v1/autos")
    assert response.status_code == 403  # Access forbidden

# Test searching cars as 'owner' (should succeed)
def test_search_auto_with_owner():
    set_user_role("owner")
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 200
    results = response.json()
    for auto in results:
        assert "BMW" in auto["brand"]  # Each result must match search criteria

# Test searching cars as 'customer' (should succeed)
def test_search_auto_with_customer():
    set_user_role("customer")
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 200
    results = response.json()
    for auto in results:
        assert "BMW" in auto["brand"]

# Test searching cars as 'guest' (should be forbidden)
def test_search_auto_with_guest():
    set_user_role("guest")
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 403

# Test fetching a specific car by ID as 'owner' (should succeed)
def test_show_auto_by_id_with_owner():
    set_user_role("owner")
    auto = {
        "brand": "Audi",
        "model": "coupe",
        "jahr": 2010,
        "preis_pro_stunde": 40,
        "status": True
    }
    create_resp = client.post("/api/v1/auto", json=auto)
    auto_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/autos/{auto_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == auto_id
    assert data["brand"] == "Audi"

# Test fetching a car by ID as 'guest' (should be forbidden)
def test_show_auto_by_id_with_guest():
    set_user_role("guest")
    response = client.get("/api/v1/autos/1")
    assert response.status_code == 403

# Test updating a car as 'owner' (should succeed)
def test_update_auto_with_owner():
    set_user_role("owner")
    create_resp = client.post("/api/v1/auto", json=auto_template)
    auto_id = create_resp.json()["id"]

    update_data = {
        "preis_pro_stunde": 35,
        "status": False
    }
    update_resp = client.put(f"/api/v1/autos/{auto_id}", json=update_data)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["preis_pro_stunde"] == 35
    assert updated["status"] is False

# Test updating a car as 'customer' (should be forbidden)
def test_update_auto_with_customer_forbidden():
    set_user_role("customer")
    update_data = {
        "brand": "Audi"
    }
    response = client.put("/api/v1/autos/1", json=update_data)
    assert response.status_code == 403

# Test updating a car as 'guest' (should be forbidden)
def test_update_auto_with_guest_forbidden():
    set_user_role("guest")
    update_data = {
        "brand": "Audi"
    }
    response = client.put("/api/v1/autos/1", json=update_data)
    assert response.status_code == 403

# Test deleting a car as 'owner' (should succeed)
def test_delete_auto_with_owner():
    set_user_role("owner")
    create_resp = client.post("/api/v1/auto", json=auto_template)
    auto_id = create_resp.json()["id"]

    response = client.delete(f"/api/v1/autos/{auto_id}")
    assert response.status_code == 204  # No content, deleted successfully

# Test deleting a car as 'customer' (should be forbidden)
def test_delete_auto_with_customer_forbidden():
    set_user_role("customer")
    response = client.delete("/api/v1/autos/1")
    assert response.status_code == 403

# Test deleting a car as 'guest' (should be forbidden)
def test_delete_auto_with_guest_forbidden():
    set_user_role("guest")
    response = client.delete("/api/v1/autos/1")
    assert response.status_code == 403

# Test calculating rental price as 'owner' (should succeed)
def test_calculate_price_with_owner():
    set_user_role("owner")
    create_resp = client.post("/api/v1/auto", json=auto_template)
    auto_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total_price"] == 30 * 5  # price per hour * hours rented
