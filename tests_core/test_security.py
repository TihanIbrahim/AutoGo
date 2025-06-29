from security.hash import verify, hash_password
from security.jwt import create_token, SECRET_KEY, ALGORITHM, decode_token
from jose import jwt
from datetime import timedelta, datetime
import pytest
from fastapi import HTTPException

# Testet das Hashen und Verifizieren von Passwörtern
def test_hashpassword_verify():
    password = "Test-password-1@"
    hashed_password = hash_password(password)
    
    # Das gehashte Passwort sollte nicht mit dem Klartextpasswort identisch sein
    assert hashed_password != password
    
    # Verifikation gibt True zurück, wenn das Passwort korrekt ist
    assert verify(password, hashed_password)
    
    # Verifikation gibt False zurück, wenn das Passwort falsch ist
    assert not verify("falsche password", hashed_password)

# Testet die Erstellung und das Decodieren eines JWT-Tokens
def test_create_token_contents():
    token = create_token(
        email="titor9412@gmail.com",
        user_id=0,
        expires_delta=timedelta(minutes=30)
    )
    
    # JWT-Token decodieren und Inhalte im Payload prüfen
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "titor9412@gmail.com"
    assert payload.get("id") == 0
    assert len(token) > 0
    assert isinstance(token, str)

# Testet, ob ein abgelaufener Token eine HTTPException wirft
def test_expired_token():
    token = create_token(
        email="tihanibrahim@gmail.com",
        user_id=12345,
        expires_delta=timedelta(seconds=-1)  # Token ist bereits abgelaufen
    )
    with pytest.raises(HTTPException) as error:
        decode_token(token)
    # Erwartet wird ein 401 Unauthorized Fehler
    assert error.value.status_code == 401

# Testet, ob das Decodieren eines Tokens ohne erforderliche Felder eine HTTPException auslöst
def test_token_missing_fields():
    # Erstelle ein Token nur mit Ablaufdatum, ohne 'sub' und 'id'
    token_missing_fields = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    with pytest.raises(HTTPException) as error:
        decode_token(token_missing_fields)
    # Erwartet wird ein 401 Unauthorized Fehler
    assert error.value.status_code == 401
