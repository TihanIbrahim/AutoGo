import pytest
from fastapi.testclient import TestClient
from main import app
from tests_app.helpers import set_user_role
import secrets


client = TestClient(app)

# ---------- Hilfsfunktionen ----------

def get_kunden_template():
    # Gibt ein Beispiel-Kunden-Datenobjekt zurück mit einer zufälligen E-Mail,
    # damit keine Duplikate bei den Tests entstehen
    random_num= secrets.randbelow(100000) + 1 
    return {
        "vorname": "Test",
        "nachname": "User",
        "geb_datum": "2000-01-01",
        "handy_nummer": "0123456789",
        "email": f"user{random_num}@gmail.com"
    }

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    # Setzt automatisch nach jedem Test die Dependency-Overrides von FastAPI zurück,
    # damit sich Tests nicht gegenseitig beeinflussen
    yield
    app.dependency_overrides = {}

@pytest.fixture
def created_kunde():
    # Erzeugt einen Kunden mit der Rolle 'customer' und gibt das erstellte Objekt zurück,
    # damit andere Tests dieses nutzen können
    set_user_role("customer")
    data = get_kunden_template()
    response = client.post("/api/v1/kunden", json=data)
    assert response.status_code == 201
    return response.json()

# ---------- Tests ----------

# --- Test zum Erstellen von Kunden mit unterschiedlichen Benutzerrollen ---
@pytest.mark.parametrize("role, expected_status", [
    ("customer", 201),
    ("guest", 201),
])
def test_create_kunden_permissions(role, expected_status):
    # Prüft, ob verschiedene Benutzerrollen Kunden anlegen können
    set_user_role(role)
    response = client.post("/api/v1/kunden", json=get_kunden_template())
    assert response.status_code == expected_status
