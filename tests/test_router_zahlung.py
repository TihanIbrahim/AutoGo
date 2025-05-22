import pytest
from fastapi.testclient import TestClient
from main import app
import random

client = TestClient(app)

@pytest.fixture
def auto_id():
    # Create a new car and return its ID
    auto = {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2007,
        "preis_pro_stunde": 30,
        "status": True
    }
    response = client.post("/api/v1/auto", json=auto)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def kunde_id():
    # Create a new customer and return its ID
    kunde = {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": "2000-08-25",
        "handy_nummer": "0947698022",
        "email": f"user{random.randint(1,100000)}@gmail.com"
    }
    response = client.post("/api/v1/kunde", json=kunde)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def vertrag_id(auto_id, kunde_id):
    # Create a new contract linked to car and customer, return its ID
    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunde_id,
        "status": True,
        "beginnt_datum": "2000-05-25",
        "beendet_datum": "2000-06-25",
        "total_preis": 500
    }
    response = client.post("/api/v1/vertrag", json=vertrag)
    assert response.status_code == 201
    return response.json()["id"]

def test_create_zahlung(vertrag_id):
    # Test creating a payment
    zahlung= {
        "vertragid": vertrag_id, 
        "zahlungsmethode": "direkt überweisung", 
        "datum": "2025-03-11",  
        "status": "wurde überwiesen",
        "betrag": 300.0
    }
    
    zahlung_response = client.post("/api/v1/zahlung", json=zahlung)
    assert zahlung_response.status_code == 201
    zahlung_data = zahlung_response.json()

    # Verify the payment data matches the input
    assert zahlung_data["vertragid"] == vertrag_id
    assert zahlung_data["zahlungsmethode"] == "direkt überweisung"
    assert zahlung_data["datum"] == "2025-03-11"
    assert zahlung_data["status"] == "wurde überwiesen"
    assert zahlung_data["betrag"] == 300.0

def test_list_zahlungen(vertrag_id):
    # Create a payment to ensure at least one exists
    zahlung = {
        "vertragid": vertrag_id, 
        "zahlungsmethode": "direkt überweisung", 
        "datum": "2025-03-11",  
        "status": "wurde überwiesen",
        "betrag": 300.0
    }
    zahlung_response = client.post("/api/v1/zahlung", json=zahlung)
    assert zahlung_response.status_code == 201

    # Retrieve all payments and verify the list contains at least one
    list_response = client.get("/api/v1/zahlungen")
    assert list_response.status_code == 200

    zahlungen = list_response.json()
    assert isinstance(zahlungen, list)
    assert len(zahlungen) > 0

    # Check that the created payment is present in the list
    found = False
    for z in zahlungen:
        if z["vertragid"] == vertrag_id and z["betrag"] == 300.0:
            found = True
            break

    assert found, "The created payment was not found in the list"

def test_suchen_zahlungen_id(vertrag_id):
    # Create a payment and retrieve it by ID
    zahlung = {
        "vertragid": vertrag_id,
        "zahlungsmethode": "direkt überweisung",
        "datum": "2025-03-11",
        "status": "wurde überwiesen",
        "betrag": 300.0
    }
    zahlung_response = client.post("/api/v1/zahlung", json=zahlung)
    assert zahlung_response.status_code == 201
    zahlung_id = zahlung_response.json()["id"]

    zahlung_id_response = client.get(f"/api/v1/zahlungen/{zahlung_id}")
    assert zahlung_id_response.status_code == 200
    zahlung_data1 = zahlung_id_response.json()

    # Verify the fetched payment data matches the original
    assert zahlung_data1["vertragid"] == vertrag_id
    assert zahlung_data1["zahlungsmethode"] == "direkt überweisung"
    assert zahlung_data1["datum"] == "2025-03-11"
    assert zahlung_data1["status"] == "wurde überwiesen"
    assert zahlung_data1["betrag"] == 300.0

def test_update_zahlung(vertrag_id):
    # Create a payment then update it
    zahlung = {
        "vertragid": vertrag_id,
        "zahlungsmethode": "direkt überweisung",
        "datum": "2025-03-11",
        "status": "wurde überwiesen",
        "betrag": 300.0
    }
    zahlung_response = client.post("/api/v1/zahlung", json=zahlung)
    assert zahlung_response.status_code == 201
    zahlung_id = zahlung_response.json()["id"]

    zahlung_update = {
        "vertragid": vertrag_id,
        "zahlungsmethode": "direkt überweisung",
        "datum": "2025-02-11",
        "status": "wurde überwiesen",
        "betrag": 320.0
    }

    zahlung_id_update_response = client.put(f"/api/v1/zahlungen/{zahlung_id}", json=zahlung_update)
    assert zahlung_id_update_response.status_code == 200
    updated_data = zahlung_id_update_response.json()
    
    # Confirm the payment was updated correctly
    assert updated_data["datum"] == "2025-02-11"
    assert updated_data["betrag"] == 320.0

def test_delete_zahlung(vertrag_id):
    # Create a payment then delete it
    zahlung = {
        "vertragid": vertrag_id,
        "zahlungsmethode": "direkt überweisung",
        "datum": "2025-03-11",
        "status": "wurde überwiesen",
        "betrag": 300.0
    }
    zahlung_response = client.post("/api/v1/zahlung", json=zahlung)
    assert zahlung_response.status_code == 201
    zahlung_id = zahlung_response.json()["id"]

    delete_response = client.delete(f"/api/v1/zahlungen/{zahlung_id}")
    assert delete_response.status_code == 204  

    # Verify that the deleted payment is no longer retrievable
    get_response = client.get(f"/api/v1/zahlung/{zahlung_id}")
    assert get_response.status_code == 404       
