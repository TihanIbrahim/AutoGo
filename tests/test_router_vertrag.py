from fastapi.testclient import TestClient
from datetime import date
from main import app
import random
import pytest

client = TestClient(app)

@pytest.fixture
def create_auto_kunde():
    # Prepare sample auto data
    auto = {
        "brand": "TOYOTA",
        "model": "COROLA",
        "jahr": 2023,
        "preis_pro_stunde": 15,
        "status": True
    }

    # Prepare sample kunde (customer) data with a random email to avoid conflicts
    kunde = {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random.randint(1,100000)}@gmail.com"
    }

    # Create the auto via API
    response_create_Auto = client.post("/api/v1/auto", json=auto)
    # Create the kunde via API
    response_create_kunde = client.post("/api/v1/kunde", json=kunde)

    # Verify both creations succeeded with HTTP 201 Created
    assert response_create_Auto.status_code == 201
    assert response_create_kunde.status_code == 201

    # Return the created auto and kunde IDs for use in dependent tests
    return response_create_Auto.json()["id"], response_create_kunde.json()["id"]

def test_create_vertrag(create_auto_kunde):
    # Receive auto_id and kunden_id from the fixture
    auto_id, kunden_id = create_auto_kunde

    # Prepare contract (vertrag) data linking auto and kunde with dates and total price
    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 8, 17)),
        "beendet_datum": str(date(2025, 9, 17)),
        "total_preis": 274.6,
        "status": True
    }

    # Create the contract via POST request
    response_vertrag = client.post("/api/v1/vertrag", json=vertrag)
    # Expect HTTP 201 Created on success
    assert response_vertrag.status_code == 201

    data = response_vertrag.json()
    # Verify the returned contract data matches the input and IDs
    assert data["auto_id"] == auto_id
    assert data["kunden_id"] == kunden_id
    assert data["beginnt_datum"] == "2025-08-17"
    assert data["beendet_datum"] == "2025-09-17"
    assert data["total_preis"] == 274.6
    assert data["status"] is True

def test_vertrag_kundigen(create_auto_kunde):
    # Get the IDs of created auto and kunde from fixture
    auto_id, kunden_id = create_auto_kunde

    # Create a new contract to be canceled
    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 9, 27)),
        "beendet_datum": str(date(2025, 10, 27)),
        "total_preis": 244.6,
        "status": True
    }

    # Create the contract
    response_vertrag = client.post("/api/v1/vertrag", json=vertrag)
    assert response_vertrag.status_code == 201

    # Extract the contract ID for cancellation
    vertrag_id = response_vertrag.json()["id"]

    # Send POST request to cancel (kündigen) the contract
    response_kundigen = client.post(f"/api/v1/Verträge/{vertrag_id}/kuendigen")
    # Expect HTTP 200 OK status for successful cancellation
    assert response_kundigen.status_code == 200
    # Verify the success message returned
    assert response_kundigen.json().get("message") == "Vertrag wurde erfolgreich gekündigt."

def test_vertrag_kundigen_nach_start(create_auto_kunde):
    # Receive auto and kunde IDs
    auto_id, kunden_id = create_auto_kunde

    # Create a contract that already started (past begin date)
    vertrag = {
        "auto_id": auto_id,
        "kunden_id": kunden_id,
        "beginnt_datum": str(date(2025, 5, 1)),
        "beendet_datum": str(date(2025, 5, 27)),
        "total_preis": 244.6,
        "status": True
    }

    # Create the contract via API
    response_creat_vertrag = client.post("/api/v1/vertrag", json=vertrag)
    assert response_creat_vertrag.status_code == 201
    vertrag_id = response_creat_vertrag.json()["id"]

    # Attempt to cancel the contract after it has already started
    response_kundigen_nach_start = client.post(f"/api/v1/Verträge/{vertrag_id}/kuendigen")

    # Expect HTTP 400 Bad Request since cancellation after start is not allowed
    assert response_kundigen_nach_start.status_code == 400
    # Verify the returned error message matches expected text
    assert response_kundigen_nach_start.json().get("detail") == "Kündigung nach Vertragsbeginn ist nicht möglich."
