import pytest
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role

client = TestClient(app)

# Sample car data used for creating test autos
auto_template = {
    "brand": "BMW",
    "model": "sedan",
    "jahr": 2010,
    "preis_pro_stunde": 30,
    "status": "verfügbar"
}

# Fixture to clear dependency overrides after each test to avoid side effects
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# Fixture to create a car and return its ID, created as 'owner' role
@pytest.fixture
def created_auto():
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

# Fixture to set user role before each test that requires it
@pytest.fixture
def set_role(request):
    role = request.param
    set_user_role(role)
    yield
    # any cleanup if needed

# ======= Test creating a car with different user roles =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 201),  # Owners can create cars successfully
    ("viewer", 403), # Viewers are forbidden to create
    ("editor", 403), # Editors are forbidden to create
])
def test_create_auto_by_role(role, expected_status):
    set_user_role(role)  # Set the user role for the request
    response = client.post("/api/v1/dashboard/autos", json=auto_template)  # Attempt to create a car

    assert response.status_code == expected_status

    if expected_status == 201:
        data = response.json()
        assert data["brand"] == "BMW"
        assert data["preis_pro_stunde"] == 30

# ======= Test fetching all cars with different user roles =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),  # Owners can fetch all cars
    ("viewer", 200), # Viewers can also fetch all cars
    ("editor", 403), # Editors are forbidden to fetch all cars
])
def test_show_all_auto_forbidden_roles(role, expected_status):
    set_user_role(role)
    response = client.get("/api/v1/dashboard/autos")  # Fetch all cars
    assert response.status_code == expected_status

# ======= Test fetching a car by ID with different user roles =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),  # Owners can view car details
    ("viewer", 403), # Viewers are forbidden to view car by ID
    ("editor", 403), # Editors are forbidden to view car by ID
])
def test_show_auto_by_id(role, expected_status, created_auto):
    set_user_role(role)
    response = client.get(f"/api/v1/dashboard/autos/{created_auto}")

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data["id"] == created_auto
        assert data["brand"] == "BMW"
        assert data["jahr"] == 2010
        assert data["model"] == "sedan"

# ======= Test updating a car with different user roles =======
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),  # Owners can update
    ("viewer", 403), # Viewers forbidden to update
    ("editor", 200), # Editors allowed to update
])
def test_update_auto(role, expected_status, created_auto):
    # Data to update
    update_data = {
        "brand": "bmw",
        "model": "coupe"
    }

    set_user_role(role)
    response = client.put(f"/api/v1/dashboard/autos/{created_auto}", json=update_data)

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data["brand"] == "bmw"
        assert data["model"] == "coupe"

# ======= Test deleting a car with different user roles =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 204),  # Owners can delete successfully
    ("editor", 403), # Editors forbidden to delete
    ("viewer", 403), # Viewers forbidden to delete
])
def test_delete_auto(role, expected_status, created_auto):
    set_user_role(role)
    response = client.delete(f"/api/v1/dashboard/autos/{created_auto}")
    assert response.status_code == expected_status

    # If deletion successful, verify the car is really deleted
    if expected_status == 204:
        set_user_role("owner")  # Owner to check existence
        get_resp = client.get(f"/api/v1/dashboard/autos/{created_auto}")
        assert get_resp.status_code == 404

