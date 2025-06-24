import pytest
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role


client = TestClient(app)

# Sample car data used in create car tests
auto_template = {
    "brand": "BMW",
    "model": "sedan",
    "jahr": 2010,
    "preis_pro_stunde": 30,
    "status": "verfügbar"
}

# Fixture to clear dependency overrides after each test automatically
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}


# ======= Test searching cars with different roles =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("guest", 200),
    ("customer", 200),
])
def test_search_auto(role, expected_status):
    
    set_user_role("owner")  
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert create_resp.status_code == 201

    set_user_role(role)  

    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == expected_status

    if expected_status == 200:
        results = response.json()
        assert isinstance(results, list)
        for auto in results:
            assert "brand" in auto
            assert "bmw" in auto["brand"].lower()


# ======= Test calculating rental price with different roles =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("customer", 200),
    ("guest", 200),
])
def test_calculate_price(role, expected_status):
    # Create a car as owner first to get a valid auto_id
    set_user_role("owner")
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_template)
    auto_id = create_resp.json()["id"]

    # Set the user role for testing price calculation
    set_user_role(role)

    # Make POST request to calculate rental price for 5 hours
    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=5")
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        # Verify total price calculation is correct (price per hour * rental duration)
        assert data["total_price"] == 30 * 5


# ======= Test price calculation when car is not available =======
def test_calculate_price_for_unavailable_auto():
    # Set user role as owner to create the auto
    set_user_role("owner")

    # Create a car that is currently unavailable (e.g. in maintenance)
    auto_unavailable = {
        "brand": "Tesla",
        "model": "model 3",
        "jahr": 2020,
        "preis_pro_stunde": 50,
        "status": "in_wartung"  # Not available status
    }
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_unavailable)
    auto_id = create_resp.json()["id"]
    set_user_role("customer")
    # Attempt to calculate price, expect 400 error due to unavailability
    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=3")
    assert response.status_code == 400
    assert response.json()["detail"] == "Das Auto ist momentan nicht verfügbar."


# ======= Test price calculation for non-existent car =======
def test_calculate_price_for_nonexistent_auto():
    set_user_role("customer")
    non_existent_auto_id = 99999  # ID that does not exist

    # Attempt to calculate price for a non-existent car, expect 404 error
    response = client.post(f"/api/v1/autos/{non_existent_auto_id}/calculate-price?mietdauer_stunden=2")
    assert response.status_code == 404
    assert "nicht gefunden" in response.json()["detail"]


# ======= Test invalid rental duration (<=0) =======
@pytest.mark.parametrize("invalid_duration", [0, -5])
def test_calculate_price_with_invalid_rental_duration(invalid_duration):
    set_user_role("owner")

    # Create a car to get a valid ID for testing
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_template)
    auto_id = create_resp.json()["id"]

    set_user_role("customer")
    # Attempt to calculate price with invalid rental durations, expect validation error (422)
    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden={invalid_duration}")
    assert response.status_code == 422
