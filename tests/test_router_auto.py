import pytest
from fastapi.testclient import TestClient
from main import app
from services.dependencies import get_current_user

client = TestClient(app)

# Sample car data for testing
auto_template = {
    "brand": "BMW",
    "model": "sedan",
    "jahr": 2010,
    "preis_pro_stunde": 30,
    "status": True
}

# Fake users with different roles
def fake_user_with_role_owner():
    class User:
        role = "owner"
    return User()

def fake_user_with_role_customer():
    class User:
        role = "customer"
    return User()

def fake_user_without_role():
    class User:
        role = "guest"
    return User()

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# ======= Permission and functionality tests =======

# Create car tests
def test_create_auto_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 201
    data = response.json()
    assert data["brand"] == "BMW"
    assert data["preis_pro_stunde"] == 30

def test_create_auto_with_customer():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 403

def test_create_auto_with_guest():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.post("/api/v1/auto", json=auto_template)
    assert response.status_code == 403

# Get all cars tests
def test_show_all_auto_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.get("/api/v1/autos")
    assert response.status_code == 200
    autos = response.json()
    assert isinstance(autos, list)
    assert len(autos) > 0



def test_show_all_auto_with_guest():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.get("/api/v1/autos")
    assert response.status_code == 403

# Search cars tests
def test_search_auto_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 200
    results = response.json()
    for auto in results:
        assert "BMW" in auto["brand"]

def test_search_auto_with_customer():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 200
    results = response.json()
    for auto in results:
        assert "BMW" in auto["brand"]

def test_search_auto_with_guest():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 403

# Get car by ID tests
def test_show_auto_by_id_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
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



def test_show_auto_by_id_with_guest():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.get("/api/v1/autos/1")
    assert response.status_code == 403

# Update car tests
def test_update_auto_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
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

def test_update_auto_with_customer_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    update_data = {
        "brand": "Audi"
    }
    response = client.put("/api/v1/autos/1", json=update_data)
    assert response.status_code == 403

def test_update_auto_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    update_data = {
        "brand": "Audi"
    }
    response = client.put("/api/v1/autos/1", json=update_data)
    assert response.status_code == 403

# Delete car tests
def test_delete_auto_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    create_resp = client.post("/api/v1/auto", json=auto_template)
    auto_id = create_resp.json()["id"]

    response = client.delete(f"/api/v1/autos/{auto_id}")
    assert response.status_code == 204

def test_delete_auto_with_customer_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response = client.delete("/api/v1/autos/1")
    assert response.status_code == 403

def test_delete_auto_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.delete("/api/v1/autos/1")
    assert response.status_code == 403

# Calculate rental price tests
def test_calculate_price_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    create_resp = client.post("/api/v1/auto", json=auto_template)
    auto_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=5")
    assert response.status_code == 200
    data = response.json()
    assert data["gesamtpreis"] == 30 * 5
