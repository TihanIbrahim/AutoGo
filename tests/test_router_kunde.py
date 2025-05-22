from fastapi.testclient import TestClient
from datetime import date
from main import app

client = TestClient(app)

def test_creat_kunde():
    # Prepare a new customer (kunde) payload with valid data
    kunde = {
        "vorname": "Tihan",
        "nachname": "Ibrahim",
        "geb_datum": str(date(2000, 8, 25)),  # Birthdate as string in ISO format
        "handy_nummer": "0995719489",
        "email": "titor9424@gmail.com"
    }
  
    # Send POST request to create a new kunde
    response_create_kunde = client.post("/api/v1/kunde", json=kunde)
    # Expect HTTP 201 Created status for successful creation
    assert response_create_kunde.status_code == 201 

    data = response_create_kunde.json()

    # Verify the returned data matches the input values
    assert data["vorname"] == "Tihan"
    assert data["nachname"] == "Ibrahim"
    assert data["geb_datum"] == "2000-08-25"
    assert data["handy_nummer"] == "0995719489"
    assert data["email"] == "titor9424@gmail.com"

    # Ensure the response contains an "id" field assigned by the system
    assert "id" in data

    kunde_id = data["id"]

    # Send DELETE request to remove the created kunde by ID
    response_delete_kunde = client.delete(f"/api/v1/kunden/{kunde_id}")
    # Expect HTTP 204 No Content status after successful deletion
    assert response_delete_kunde.status_code == 204  

    # Attempt to GET the deleted kunde to confirm removal
    response_get_kunde = client.get(f"/api/v1/kunden/{kunde_id}")
    # Expect HTTP 404 Not Found since the kunde no longer exists
    assert response_get_kunde.status_code == 404  
