from services.auth_service import create_user_service ,login_user
from security.hash import hash_password 
from schemas.auth_schemas import CreateRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from data_base import Base
from fastapi import HTTPException

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to set up session and database
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user(db):
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Abc123456!"
    )

    user1 = create_user_service(request1, db)

    assert user1.email == request1.email
    assert user1.hashed_password != request1.password
    assert user1.hashed_password is not None

    request2 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Abc125476!"
    )

    with pytest.raises(HTTPException) as error:
        create_user_service(request2, db)
    assert error.value.status_code == 409  


from security.hash import verify

def test_login_user(db):
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Abc123456!"
    )

    user1 = create_user_service(request1, db)

    logged_in_user = login_user(
        email="lolo1234@gmail.com",
        password="Abc123456!",
        db=db
    )

    assert logged_in_user.email == request1.email
    assert verify(request1.password, logged_in_user.hashed_password)
