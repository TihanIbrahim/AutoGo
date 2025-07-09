from services.auth_service import create_user_service, login_user
from core.security.hash import verify
from schemas.auth_schemas import CreateRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from data_base import Base
from fastapi import HTTPException

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture zur Einrichtung und Aufräumung der In-Memory-Datenbank vor und nach jedem Test
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)  # Tabellen erstellen
    db = SessionLocal()
    try:
        yield db  # Datenbanksession für Test bereitstellen
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Tabellen nach Test löschen


# Test für das Erstellen eines neuen Nutzers mit gültigen Daten
def test_create_user(db):
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-1@"
    )

    user1 = create_user_service(request1, db)

    # Verifiziere, dass der Nutzer mit gehashter (nicht roher) Passwort gespeichert wurde
    assert user1.email == request1.email
    assert user1.hashed_password != request1.password
    assert user1.hashed_password is not None

    # Versuch, denselben Nutzer nochmal zu erstellen, sollte einen Konflikt auslösen
    request2 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-1@"
    )

    with pytest.raises(HTTPException) as error:
        create_user_service(request2, db)
    assert error.value.status_code == 409  # Konflikt-Status


# Test für das Einloggen eines Nutzers mit korrekten Zugangsdaten
def test_login_user(db):
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-2@"
    )
    user1 = create_user_service(request1, db)

    logged_in_user = login_user(
        email="lolo1234@gmail.com",
        password="Test-password-2@",
        db=db
    )

    # Verifiziere, dass der geloggte Nutzer dieselbe Email hat und Passwort geprüft wurde
    assert logged_in_user.email == request1.email
    assert verify(request1.password, logged_in_user.hashed_password)


# Test für Login-Versuch mit falschem Passwort, sollte HTTP 401 zurückgeben
def test_login_user_wrong_password(db):
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-3@"
    )
    create_user_service(request1, db)

    with pytest.raises(HTTPException) as error:
        login_user(
            email="lolo1234@gmail.com",
            password="Wrong-password@",
            db=db
        )
    assert error.value.status_code == 401  # Unauthorized


# Test für Login-Versuch mit nicht existierender Email, sollte HTTP 401 zurückgeben
def test_login_user_nonexistent_email(db):
    with pytest.raises(HTTPException) as error:
        login_user(
            email="nonexistent@gmail.com",
            password="Some-password@",
            db=db
        )
    assert error.value.status_code == 401  # Unauthorized
