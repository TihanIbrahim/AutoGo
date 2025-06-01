import pytest
import random
from fastapi.testclient import TestClient
from main import app
from services.dependencies import get_current_user

client = TestClient(app)


def get_kunden_template():
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1,100000)}@gmail.com"
    }

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

# ======= Tests for creating customers =======

def test_create_kunden_with_customer():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["vorname"] == "Test"
    assert res_data["email"] == data["email"]

def test_create_kunden_with_owner_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 403

def test_create_kunden_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    data = get_kunden_template()
    response = client.post("/api/v1/kunde", json=data)
    assert response.status_code == 403

# ======= Tests for fetching all customers =======

def test_show_all_kunden_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.get("/api/v1/kunden")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_show_all_kunden_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.get("/api/v1/kunden")
    assert response.status_code == 403

# ======= Tests for fetching customer by ID =======

def test_show_kunde_by_id_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    data = get_kunden_template()
    create_resp = client.post("/api/v1/kunde", json=data)
    kunde_id = create_resp.json()["id"]

    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.get(f"/api/v1/kunden/{kunde_id}")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["id"] == kunde_id
    assert res_data["vorname"] == "Test"

def test_show_kunde_by_id_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.get("/api/v1/kunden/1")
    assert response.status_code == 403

# ======= Tests for updating a customer =======

def test_update_kunde_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    data = get_kunden_template()
    create_resp = client.post("/api/v1/kunde", json=data)
    kunde_id = create_resp.json()["id"]

    update_data = {
        "vorname": "Mohamed",
        "handy_nummer": "987654321"
    }
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.put(f"/api/v1/kunden/{kunde_id}", json=update_data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["vorname"] == "Mohamed"
    assert res_data["handy_nummer"] == "987654321"

def test_update_kunde_with_customer_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    update_data = {"vorname": "Mohamed"}
    response = client.put("/api/v1/kunden/1", json=update_data)
    assert response.status_code == 403

def test_update_kunde_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    update_data = {"vorname": "Mohamed"}
    response = client.put("/api/v1/kunden/1", json=update_data)
    assert response.status_code == 403

# ======= Tests for deleting a customer =======

def test_delete_kunde_with_owner():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    data = get_kunden_template()
    create_resp = client.post("/api/v1/kunde", json=data)
    kunde_id = create_resp.json()["id"]

    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.delete(f"/api/v1/kunden/{kunde_id}")
    assert response.status_code == 204

def test_delete_kunde_with_customer_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response = client.delete("/api/v1/kunden/1")
    assert response.status_code == 403

def test_delete_kunde_with_guest_forbidden():
    app.dependency_overrides[get_current_user] = fake_user_without_role
    response = client.delete("/api/v1/kunden/1")
    assert response.status_code == 403
