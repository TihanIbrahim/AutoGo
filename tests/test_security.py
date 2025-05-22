from security.hash import verify,hash_password
from security.jwt  import create_token ,SECRET_KEY , ALGORITHM , decode_token
from jose import jwt 
from datetime import timedelta,datetime
import pytest
from fastapi import HTTPException

def test_hashpassword_verify():
    password="tito123456789"
    hashed_password=hash_password("tito123456789")
    assert hashed_password != password
    assert verify("tito123456789",hashed_password)
    assert not verify("falsche password",hashed_password)


def test_create_token_contents():
    token = create_token(
        email="titor9412@gmail.com",
        user_id=0,
        expires_delta=timedelta(minutes=30)
    )

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "titor9412@gmail.com"
    assert payload.get("id") == 0
    assert len(token) > 0
    assert isinstance(token, str)

def test_expired_token():
    token = create_token(
        email="tihanibrahim@gmail.com",
        user_id= 12345 ,
        expires_delta = timedelta(seconds=-1) 
    )
    with pytest.raises(HTTPException) as error:
        decode_token(token)
        
    assert error.value.status_code == 401


def test_token_missing_fields():
    invalid_token = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    with pytest.raises(HTTPException) as error:
        decode_token(invalid_token)
    assert error.value.status_code == 401
