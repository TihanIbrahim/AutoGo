from services.dependencies import get_current_user
from main import app

def set_user_role(role: str):
    class User:
        def __init__(self, role):
            self.role = role
    app.dependency_overrides[get_current_user] = lambda: User(role)
