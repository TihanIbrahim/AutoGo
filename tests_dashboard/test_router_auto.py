import pytest
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role

client = TestClient(app)

# Beispiel-Daten für ein Auto, das in den Tests verwendet wird
auto_template = {
    "brand": "BMW",
    "model": "sedan",
    "jahr": 2010,
    "preis_pro_stunde": 30,
    "status": "verfügbar"
}

# Fixture, um nach jedem Test die Dependency Overrides zurückzusetzen und Seiteneffekte zu vermeiden
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# Fixture, um ein Auto zu erstellen und dessen ID zurückzugeben, mit Rolle 'owner'
@pytest.fixture
def created_auto():
    set_user_role("owner")  # Rolle auf 'owner' setzen, der Autos erstellen darf
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

# Fixture, um die Nutzerrolle vor einem Test zu setzen
@pytest.fixture
def set_role(request):
    role = request.param
    set_user_role(role)
    yield
    # Hier kann bei Bedarf aufgeräumt werden

# ======= Test: Auto erstellen mit verschiedenen Nutzerrollen =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 201),  # Owner dürfen Autos erfolgreich erstellen
    ("viewer", 403), # Viewer sind verboten, Autos zu erstellen
    ("editor", 403), # Editor sind verboten, Autos zu erstellen
])
def test_create_auto_by_role(role, expected_status):
    set_user_role(role)  # Nutzerrolle setzen
    response = client.post("/api/v1/dashboard/autos", json=auto_template)  # Versuch Auto zu erstellen

    assert response.status_code == expected_status

    if expected_status == 201:
        data = response.json()
        assert data["brand"] == "BMW"
        assert data["preis_pro_stunde"] == 30

# ======= Test: Alle Autos abrufen mit verschiedenen Nutzerrollen =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),  # Owner dürfen alle Autos abrufen
    ("viewer", 200), # Viewer dürfen ebenfalls alle Autos abrufen
    ("editor", 403), # Editor sind verboten, alle Autos abzurufen
])
def test_show_all_auto_forbidden_roles(role, expected_status):
    set_user_role(role)
    response = client.get("/api/v1/dashboard/autos")  # Alle Autos abrufen
    assert response.status_code == expected_status

# ======= Test: Auto nach ID abrufen mit verschiedenen Nutzerrollen =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),  # Owner dürfen Autodetails ansehen
    ("viewer", 403), # Viewer dürfen nicht nach ID abrufen
    ("editor", 403), # Editor dürfen nicht nach ID abrufen
])
def test_show_auto_by_id(role, expected_status, created_auto):
    set_user_role(role)
    response = client.get(f"/api/v1/dashboard/autos/{created_auto}")

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data["id"] == created_auto
        assert data["brand"] == "BMW"
        assert data["jahr"] == 2010
        assert data["model"] == "sedan"

# ======= Test: Auto aktualisieren mit verschiedenen Nutzerrollen =======
@pytest.mark.parametrize("role, expected_status", [
    ("owner", 200),  # Owner dürfen aktualisieren
    ("viewer", 403), # Viewer verboten zu aktualisieren
    ("editor", 200), # Editor dürfen aktualisieren
])
def test_update_auto(role, expected_status, created_auto):
    # Daten, die aktualisiert werden sollen
    update_data = {
        "brand": "bmw",
        "model": "coupe"
    }

    set_user_role(role)
    response = client.put(f"/api/v1/dashboard/autos/{created_auto}", json=update_data)

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data["brand"] == "bmw"
        assert data["model"] == "coupe"

# ======= Test: Auto löschen mit verschiedenen Nutzerrollen =======
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 204),  # Owner dürfen erfolgreich löschen
    ("editor", 403), # Editor verboten zu löschen
    ("viewer", 403), # Viewer verboten zu löschen
])
def test_delete_auto(role, expected_status, created_auto):
    set_user_role(role)
    response = client.delete(f"/api/v1/dashboard/autos/{created_auto}")
    assert response.status_code == expected_status

    # Falls Löschung erfolgreich war, prüfen, dass das Auto nicht mehr existiert
    if expected_status == 204:
        set_user_role("owner")  # Owner-Rolle setzen, um Verfügbarkeit zu prüfen
        get_resp = client.get(f"/api/v1/dashboard/autos/{created_auto}")
        assert get_resp.status_code == 404
