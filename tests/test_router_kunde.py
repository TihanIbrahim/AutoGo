from main import app
import pytest
from fastapi.testclient import TestClient
from datetime import date

client=TestClient(app)

def test_creat_kunde():
    kunde={
        "vorname": "Tihan" ,
        "nachname": "Ibrahim",
        "geb_datum": str(date(2000,8,25)),
        "handy_nummer": "0995719489" ,
        "email":"titor9424@gmail.com"
    }
    response_create_kunde = client.post("/api/v1/kunde",json=kunde)
    assert response_create_kunde.status_code == 200

    data=response_create_kunde.json()

    assert data["vorname"]=="Tihan"
    assert data["nachname"]=="Ibrahim"
    assert data["geb_datum"]=="2000-08-25"
    assert data["handy_nummer"]=="0995719489"
    assert data["email"]=="titor9424@gmail.com"

    assert "id" in data

    kunde_id = data["id"]
    
   
    response_delete_kunde = client.delete(f"/api/v1/kunde/{kunde_id}")
    assert response_delete_kunde.status_code == 204

    response_get_kunde = client.get(f"/api/v1/kunde/{kunde_id}")
    assert response_get_kunde.status_code == 404

