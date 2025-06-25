from security.hash import verify, hash_password
from security.jwt import create_token, SECRET_KEY, ALGORITHM, decode_token
from jose import jwt
from datetime import timedelta, datetime
import pytest
from fastapi import HTTPException

# Test password hashing and verification
def test_hashpassword_verify():
    password = "Test-password-1@"
    hashed_password = hash_password(password)
    
    # The hashed password should not be the same as the raw password
    assert hashed_password != password
    
    # Verify returns True for correct password
    assert verify(password, hashed_password)
    
    # Verify returns False for incorrect password
    assert not verify("falsche password", hashed_password)

# Test creation and decoding of JWT token
def test_create_token_contents():
    token = create_token(
        email="titor9412@gmail.com",
        user_id=0,
        expires_delta=timedelta(minutes=30)
    )
    
    # Decode the JWT token and check payload contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "titor9412@gmail.com"
    assert payload.get("id") == 0
    assert len(token) > 0
    assert isinstance(token, str)

# Test handling of expired token raises HTTPException
def test_expired_token():
    token = create_token(
        email="tihanibrahim@gmail.com",
        user_id=12345,
        expires_delta=timedelta(seconds=-1)  # Already expired token
    )
    with pytest.raises(HTTPException) as error:
        decode_token(token)
    assert error.value.status_code == 401

# Test decoding a token missing required fields raises HTTPException
def test_token_missing_fields():
    # Create a token with only expiration, missing 'sub' and 'id'
    token_missing_fields = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    with pytest.raises(HTTPException) as error:
        decode_token(token_missing_fields)
    assert error.value.status_code == 401
