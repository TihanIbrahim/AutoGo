from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

def test_create_auto():
    payload = {
        "brand": "BMW",
        "model": "Sedan",
        "jahr": 2006,
        "preis_pro_stunde": 30,
        "status": True
    }
    response = client.post("/api/v1/auto", json=payload)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["brand"] == "BMW"
    assert response_data["model"] == "Sedan"
    assert response_data["jahr"] == 2006
    assert response_data["preis_pro_stunde"] == 30
    assert response_data["status"] is True
    assert "id" in response_data


def test_show_all_autos():
    
    auto1 = {
        "brand": "BMW",
        "model": "X5",
        "jahr": 2019,
        "preis_pro_stunde": 40,
        "status": True
    }

    auto2 = {
        "brand": "Audi",
        "model": "A4",
        "jahr": 2020,
        "preis_pro_stunde": 35,
        "status": True
    }

    auto3 = {
        "brand": "Mercedes",
        "model": "C-Class",
        "jahr": 2018,
        "preis_pro_stunde": 38,
        "status": False
    }
    client.post("/api/v1/auto", json=auto1)
    client.post("/api/v1/auto", json=auto2)
    client.post("/api/v1/auto", json=auto3)

    response = client.get("/api/v1/autos")
    assert response.status_code == 200
    autos = response.json()

    for auto in autos:
        assert auto["status"] is True


def test_search_auto():
    auto = {
        "brand": "Audi",
        "model": "A8",
        "jahr": 2019,
        "preis_pro_stunde": 48,
        "status": True
    }

    response = client.post("/api/v1/auto", json=auto)
    assert response.status_code == 200

    response = client.get("/api/v1/auto/search", params={"brand": "Audi"})
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    found = False
    for auto in data:
        if auto["brand"] == "Audi":
            found = True
            break

    assert found

    response = client.get("/api/v1/auto/search", params={"brand": "nicht vorhanden"})
    assert response.status_code == 404


def test_search_auto_by_id():
    auto = {
        "brand": "BMW",
        "model": "Sedan",
        "jahr": 2006,
        "preis_pro_stunde": 30,
        "status": True
    }

   
    create_response = client.post("/api/v1/auto", json=auto)
    assert create_response.status_code == 200

   
    auto_data = create_response.json()
    auto_id = auto_data["id"]
    print(f"Created auto with ID: {auto_id}") 

    
    response = client.get(f"/api/v1/auto/{auto_id}")  
  

    
    assert response.status_code == 200
