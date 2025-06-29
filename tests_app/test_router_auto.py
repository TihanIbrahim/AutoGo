import pytest
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role

client = TestClient(app)

# Beispiel-Autodaten, die in den Create-Auto-Tests verwendet werden
auto_template = {
    "brand": "BMW",
    "model": "sedan",
    "jahr": 2010,
    "preis_pro_stunde": 30,
    "status": "verfügbar"
}

# Fixture, um Dependency-Overrides nach jedem Test automatisch zurückzusetzen
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# ======= Test: Autosuche mit verschiedenen Benutzerrollen =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("guest", 200),
    ("customer", 200),
])
def test_search_auto(role, expected_status):
    # Auto als "owner" anlegen
    set_user_role("owner")  
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert create_resp.status_code == 201

    # Rolle für den Test setzen
    set_user_role(role)  

    # Auto-Suche mit Filter "brand=BMW"
    response = client.get("/api/v1/autos/search?brand=BMW")
    assert response.status_code == expected_status

    if expected_status == 200:
        results = response.json()
        assert isinstance(results, list)
        # Überprüfen, ob die Marke korrekt im Ergebnis enthalten ist
        for auto in results:
            assert "brand" in auto
            assert "bmw" in auto["brand"].lower()

# ======= Test: Berechnung des Mietpreises mit verschiedenen Rollen =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("customer", 200),
    ("guest", 200),
])
def test_calculate_price(role, expected_status):
    # Auto als "owner" anlegen, um gültige auto_id zu erhalten
    set_user_role("owner")
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_template)
    auto_id = create_resp.json()["id"]

    # Rolle für Preiskalkulation setzen
    set_user_role(role)

    # Mietpreis für 5 Stunden berechnen
    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=5")
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        # Überprüfen, ob der Gesamtpreis korrekt berechnet wurde (Preis pro Stunde * Mietdauer)
        assert data["total_price"] == 30 * 5

# ======= Test: Preisberechnung für nicht verfügbares Auto =======
def test_calculate_price_for_unavailable_auto():
    # Auto als "owner" mit Status 'in_wartung' anlegen
    set_user_role("owner")

    auto_unavailable = {
        "brand": "Tesla",
        "model": "model 3",
        "jahr": 2020,
        "preis_pro_stunde": 50,
        "status": "in_wartung"  # Auto nicht verfügbar
    }
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_unavailable)
    auto_id = create_resp.json()["id"]

    # Rolle auf "customer" setzen und Preisberechnung versuchen
    set_user_role("customer")
    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden=3")

    # Erwarteter Fehler: Auto nicht verfügbar
    assert response.status_code == 400
    assert response.json()["detail"] == "Das Auto ist momentan nicht verfügbar."

# ======= Test: Preisberechnung für nicht existierendes Auto =======
def test_calculate_price_for_nonexistent_auto():
    set_user_role("customer")
    non_existent_auto_id = 99999  # ID, die nicht existiert

    # Preisberechnung versuchen, Fehler 404 erwartet
    response = client.post(f"/api/v1/autos/{non_existent_auto_id}/calculate-price?mietdauer_stunden=2")
    assert response.status_code == 404
    assert "nicht gefunden" in response.json()["detail"]

# ======= Test: Ungültige Mietdauer (<=0) =======
@pytest.mark.parametrize("invalid_duration", [0, -5])
def test_calculate_price_with_invalid_rental_duration(invalid_duration):
    # Auto als "owner" anlegen
    set_user_role("owner")
    create_resp = client.post("/api/v1/dashboard/autos", json=auto_template)
    auto_id = create_resp.json()["id"]

    # Rolle auf "customer" setzen
    set_user_role("customer")

    # Preisberechnung mit ungültiger Mietdauer, Validierungsfehler (422) erwartet
    response = client.post(f"/api/v1/autos/{auto_id}/calculate-price?mietdauer_stunden={invalid_duration}")
    assert response.status_code == 422
