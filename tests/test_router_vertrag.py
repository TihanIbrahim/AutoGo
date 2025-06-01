import pytest
from fastapi.testclient import TestClient
from datetime import date
from main import app
from services.dependencies import get_current_user
from models.user import User
import random

client = TestClient(app)

# ===== Fake users with roles for testing =====
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

# ===== Automatically reset overrides after each test =====
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# ===== Fixture to create both car and customer =====
@pytest.fixture
def create_auto_kunde():
    auto = {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": True
    }

    kunde = {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1, 100000)}@gmail.com"
    }

    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response_auto = client.post("/api/v1/auto", json=auto)

    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response_kunde = client.post("/api/v1/kunde", json=kunde)

    assert response_auto.status_code == 201
    assert response_kunde.status_code == 201

    return response_auto.json()["id"], response_kunde.json()["id"]

# ===== Contract creation test =====
def test_create_vertrag(create_auto_kunde):
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 8, 17)),
        "beendet_datum": str(date(2025, 9, 17)),
        "total_preis": 274.6,
        "status": True
    }

    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 201

    data = response.json()
    assert data["auto_id"] == auto_id
    assert data["kunden_id"] == kunden_id
    assert data["beginnt_datum"] == "2025-08-17"
    assert data["beendet_datum"] == "2025-09-17"
    assert data["total_preis"] == 274.6
    assert data["status"] is True

# ===== Contract cancellation before start date =====
def test_vertrag_kundigen(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 9, 27)),
        "beendet_datum": str(date(2025, 10, 27)),
        "total_preis": 244.6,
        "status": True
    }

    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    response_kundigen = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert response_kundigen.status_code == 200
    assert response_kundigen.json().get("message") == "Vertrag wurde erfolgreich gekündigt."

# ===== Contract cancellation after start date should fail =====
def test_vertrag_kundigen_nach_start(create_auto_kunde):
    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 5, 1)),
        "beendet_datum": str(date(2025, 5, 27)),
        "total_preis": 244.6,
        "status": True
    }

    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    response_kundigen = client.post(f"/api/v1/vertraege/{vertrag_id}/kuendigen")
    assert response_kundigen.status_code == 400
    assert response_kundigen.json().get("detail") == "Kündigung nach Vertragsbeginn ist nicht möglich."

# ===== Update existing contract =====
def test_update_vertrag(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 10, 1)),
        "beendet_datum": str(date(2025, 10, 30)),
        "total_preis": 300.0,
        "status": True
    }

    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201
    vertrag_id = response_create.json()["id"]

    update_data = {
        "total_preis": 350.0,
        "status": False
    }

    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response_update = client.put(f"/api/v1/vertraege/{vertrag_id}", json=update_data)
    assert response_update.status_code == 200

    updated_vertrag = response_update.json()
    assert updated_vertrag["total_preis"] == 350.0
    assert updated_vertrag["status"] is False

# ===== Retrieve all contracts and ensure created one exists =====
def test_get_all_vertraege(create_auto_kunde):
    auto_id, kunden_id = create_auto_kunde

    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 11, 1)),
        "beendet_datum": str(date(2025, 11, 30)),
        "total_preis": 302.0,
        "status": True
    }

    app.dependency_overrides[get_current_user] = fake_user_with_role_customer
    response_create = client.post("/api/v1/vertrag", json=vertrag)
    assert response_create.status_code == 201

    app.dependency_overrides[get_current_user] = fake_user_with_role_owner
    response_get_vertraege = client.get("/api/v1/vertraege")
    assert response_get_vertraege.status_code == 200

    data = response_get_vertraege.json()
    assert isinstance(data, list)
    assert 302.0 in [v["total_preis"] for v in data]  # Ensure the created contract is in the list

