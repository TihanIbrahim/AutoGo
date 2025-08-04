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

# Fixture: Setzt dependency overrides nach jedem Test zurück
@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides = {}

# Fixture: Erstellt ein Auto mit der Rolle 'owner' und gibt die ID zurück
@pytest.fixture
def created_auto():
    set_user_role("owner")
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == 201
    return response.json()["id"]

# ===================== Tests =====================

# Test: Auto erstellen mit verschiedenen Nutzerrollen
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 201),
    ("viewer", 403),
    ("editor", 403),
])
def test_create_auto_by_role(role, expected_status):
    set_user_role(role)
    response = client.post("/api/v1/dashboard/autos", json=auto_template)
    assert response.status_code == expected_status

    if expected_status == 201:
        data = response.json()
        assert data["brand"] == "BMW"
        assert data["preis_pro_stunde"] == 30

# Test: Alle Autos abrufen mit verschiedenen Nutzerrollen
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),
    ("viewer", 200),
    ("editor", 403),
])
def test_show_all_auto_forbidden_roles(role, expected_status):
    set_user_role(role)
    response = client.get("/api/v1/dashboard/autos")
    assert response.status_code == expected_status

# Test: Auto nach ID abrufen mit verschiedenen Nutzerrollen
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),
    ("viewer", 403),
    ("editor", 403),
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

# Test: Auto aktualisieren mit verschiedenen Nutzerrollen
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 200),
    ("viewer", 403),
    ("editor", 200),
])
def test_update_auto(role, expected_status, created_auto):
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

# Test: Auto löschen mit verschiedenen Nutzerrollen
@pytest.mark.parametrize(("role", "expected_status"), [
    ("owner", 204),
    ("editor", 403),
    ("viewer", 403),
])
def test_delete_auto(role, expected_status, created_auto):
    set_user_role(role)
    response = client.delete(f"/api/v1/dashboard/autos/{created_auto}")
    assert response.status_code == expected_status

    if expected_status == 204:
        # Prüfen, ob das Auto tatsächlich gelöscht wurde
        set_user_role("owner")
        get_resp = client.get(f"/api/v1/dashboard/autos/{created_auto}")
        assert get_resp.status_code == 404
