import pytest
from fastapi.testclient import TestClient
from main import app
from services.dependencies import get_current_user
import random

client = TestClient(app)

# ======== Fixtures for creating basic data templates ========

@pytest.fixture
def auto_template():
    # Template data for creating a car (auto)
    return {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2010,
        "preis_pro_stunde": 30,
        "status": True
    }

@pytest.fixture
def generate_kunden_data():
    # Template data for creating a customer (kunde) with random email to avoid conflicts
    return {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": "2000-08-25",
        "handy_nummer": "0995719489",
        "email": f"titor{random.randint(1, 1000000)}@gmail.com"
    }

@pytest.fixture
def zahlung_template():
    # Template data for creating a payment (zahlung)
    return {
        "zahlungsmethode": "direkt überweisung",
        "datum": "2025-06-01",
        "status": "wurde überwiesen",
        "betrag": 300.0
    }

# ======== Fixtures for creating actual API resources and returning their IDs ========

@pytest.fixture
def auto_id(auto_template):
    # Override user dependency with 'owner' role for this request
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    # Create a car and return its ID
    resp = client.post("/api/v1/auto", json=auto_template)
    assert resp.status_code == 201
    return resp.json()["id"]

@pytest.fixture
def kunde_id(generate_kunden_data):
    # Override user dependency with 'customer' role for this request
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    # Create a customer and return its ID
    resp = client.post("/api/v1/kunde", json=generate_kunden_data)
    assert resp.status_code == 201
    return resp.json()["id"]

@pytest.fixture
def vertrag_id(auto_id, kunde_id):
    # Create a contract linking the car and customer, return contract ID
    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunde_id,
        "beginnt_datum": "2025-06-01",
        "beendet_datum": "2025-06-05",
        "status": True,
        "total_preis": 120.0
    }
    # Use 'customer' role to create contract
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    resp = client.post("/api/v1/vertrag", json=vertrag)
    assert resp.status_code == 201
    return resp.json()["id"]

# ======== Fake user objects to simulate different user roles ========

def fake_user_with_role_customer():
    class User:
        role = "customer"
    return User()

def fake_user_with_role_owner():
    class User:
        role = "owner"
    return User()

def fake_user_with_role_guest():
    class User:
        role = "guest"
    return User()

# ======== Automatically clear dependency overrides after each test ========

@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides = {}

# ======== Tests for payment (zahlung) endpoints with role-based access control ========

def test_create_zahlung_with_customer(auto_id, kunde_id, vertrag_id, zahlung_template):

    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    zahlung_data = zahlung_template.copy()

    zahlung_data["vertragid"] = vertrag_id

    response = client.post("/api/v1/zahlung", json=zahlung_data)


    assert response.status_code == 201

    data = response.json()
    assert data["vertragid"] == vertrag_id
    assert data["zahlungsmethode"] == zahlung_data["zahlungsmethode"]
    assert data["betrag"] == zahlung_data["betrag"]



def test_create_zahlung_with_owner(auto_id, kunde_id, vertrag_id, zahlung_template):
    # 'owner' role attempts to create payment, which should be forbidden
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner

    zahlung_data = zahlung_template.copy()
    zahlung_data["vertragid"] = vertrag_id

    response = client.post("/api/v1/zahlung", json=zahlung_data)
    # Owner should NOT be allowed to create payment
    assert response.status_code == 403

def test_create_zahlung_with_guest(auto_id, kunde_id, vertrag_id, zahlung_template):
    # 'guest' role attempts to create payment, should be forbidden
    app.dependency_overrides[get_current_user] = fake_user_with_role_guest

    zahlung_data = zahlung_template.copy()
    zahlung_data["vertragid"] = vertrag_id

    response = client.post("/api/v1/zahlung", json=zahlung_data)
    assert response.status_code == 403

def test_list_zahlungen_with_owner():
    # Owner can list all payments
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response = client.get("/api/v1/zahlungen")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_zahlungen_with_customer():
    # Customer cannot list all payments
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response = client.get("/api/v1/zahlungen")
    assert response.status_code == 403

def test_list_zahlungen_with_guest():
    # Guest cannot list payments
    app.dependency_overrides[get_current_user] = fake_user_with_role_guest
    response = client.get("/api/v1/zahlungen")
    assert response.status_code == 403

def test_update_zahlung_with_owner(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Create payment first as customer
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertragid"] = vertrag_id
    zahlung_resp = client.post("/api/v1/zahlung", json=zahlung_data)
    assert zahlung_resp.status_code == 201
    zahlung_id = zahlung_resp.json()["id"]

    # Owner updates the payment (only amount)
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    zahlung_update = zahlung_template.copy()
    zahlung_update["betrag"] = 350.0
    zahlung_update["vertragid"] = vertrag_id  

    response = client.put(f"/api/v1/zahlungen/{zahlung_id}", json=zahlung_update)
    assert response.status_code == 200

    updated = response.json()
    assert updated["betrag"] == 350.0
    assert updated["datum"] == zahlung_template["datum"]



def test_update_zahlung_with_customer(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Customer creates and updates the payment (only amount)
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertragid"] = vertrag_id
    zahlung_resp = client.post("/api/v1/zahlung", json=zahlung_data)
    assert zahlung_resp.status_code == 201
    zahlung_id = zahlung_resp.json()["id"]

    zahlung_update = zahlung_template.copy()
    zahlung_update["betrag"] = 400.0
    zahlung_update["vertragid"] = vertrag_id

    response = client.put(f"/api/v1/zahlungen/{zahlung_id}", json=zahlung_update)
    assert response.status_code == 200

    updated = response.json()
    assert updated["betrag"] == 400.0
    assert updated["datum"] == zahlung_template["datum"]



def test_update_zahlung_with_guest():
    # Guest tries to update payment - should be forbidden
    app.dependency_overrides[get_current_user] = fake_user_with_role_guest
    response = client.put("/api/v1/zahlungen/1", json={
        "vertragid": 1,
        "zahlungsmethode": "karte",
        "datum": "2025-05-01",
        "status": "ok",
        "betrag": 100.0
    })
    assert response.status_code == 403


def test_delete_zahlung_with_owner(auto_id, kunde_id, vertrag_id, zahlung_template):
    # Create payment as customer
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    zahlung_data = zahlung_template.copy()
    zahlung_data["vertragid"] = vertrag_id
    resp = client.post("/api/v1/zahlung", json=zahlung_data)
    assert resp.status_code == 201
    zahlung_id = resp.json()["id"]

    # Owner deletes the payment
    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    delete_resp = client.delete(f"/api/v1/zahlungen/{zahlung_id}")
    assert delete_resp.status_code == 204

def test_delete_zahlung_with_customer():
    # Customer tries to delete a payment, should be forbidden
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response = client.delete("/api/v1/zahlungen/1")
    assert response.status_code == 403

def test_delete_zahlung_with_guest():
    # Guest tries to delete a payment, should be forbidden
    app.dependency_overrides[get_current_user] = fake_user_with_role_guest
    response = client.delete("/api/v1/zahlungen/1")
    assert response.status_code == 403
