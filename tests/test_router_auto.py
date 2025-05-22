import pytest
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

def test_create_auto():
    # Test successfully creating a new auto
    auto = {
        "brand": "BMW",
        "model": "sedan",
        "jahr": 2007,
        "preis_pro_stunde": 30,
        "status": True
    }
    response = client.post("/api/v1/auto", json=auto)
    # Verify the response status code is 201 Created
    assert response.status_code == 201
    data = response.json()
    # Confirm the returned data matches the input values
    assert data["brand"] == "BMW"
    assert data["preis_pro_stunde"] == 30

def test_show_all_auto():
    # Test fetching all autos successfully
    response = client.get("/api/v1/autos")
    assert response.status_code == 200
    autos = response.json()
    # Check that the result is a list and it contains at least one auto
    assert isinstance(autos, list)
    assert len(autos) > 0

def test_search_auto():
    # Test searching autos by brand
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == 200
    results = response.json()
    # Verify every returned auto has the brand containing "BMW"
    for auto in results:
        assert "BMW" in auto["brand"]

def test_show_auto_by_id():
    # Test retrieving an auto by its ID
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
    # Confirm the fetched auto has the correct ID and brand
    assert data["id"] == auto_id
    assert data["brand"] == "Audi"

def test_update_auto():
    # Test updating an existing auto's details
    auto = {
        "brand": "VW",
        "model": "hatchback",
        "jahr": 2015,
        "preis_pro_stunde": 25,
        "status": True
    }
    create_resp = client.post("/api/v1/auto", json=auto)
    auto_id = create_resp.json()["id"]

    update_data = {
        "preis_pro_stunde": 35,
        "status": False
    }
    update_resp = client.put(f"/api/v1/autos/{auto_id}", json=update_data)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    # Check that the price and status were updated correctly
    assert updated["preis_pro_stunde"] == 35
    assert updated["status"] is False

def test_calculate_price():
    # Test calculating total rental price for a given rental duration (hours)
    auto = {
        "brand": "Tesla",
        "model": "model 3",
        "jahr": 2020,
        "preis_pro_stunde": 50,
        "status": True
    }
    create_resp = client.post("/api/v1/auto", json=auto)
    auto_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=5")
    assert response.status_code == 200
    data = response.json()
    # Total price = hourly rate * number of hours rented
    assert data["gesamtpreis"] == 50 * 5

# Error Handling Tests

def test_get_auto_not_found():
    # Test fetching a non-existent auto returns 404 Not Found
    response = client.get("/api/v1/autos/999999")
    assert response.status_code == 404

def test_update_auto_not_found():
    # Test updating a non-existent auto returns 404 Not Found
    update_data = {
        "preis_pro_stunde": 40,
        "status": False
    }
    response = client.put("/api/v1/autos/999999", json=update_data)
    assert response.status_code == 404

def test_delete_auto_not_found():
    # Test deleting a non-existent auto returns 404 Not Found
    response = client.delete("/api/v1/autos/999999")
    assert response.status_code == 404
