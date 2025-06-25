from services.auth_service import create_user_service, login_user
from security.hash import hash_password, verify
from schemas.auth_schemas import CreateRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from data_base import Base
from fastapi import HTTPException

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to setup and teardown in-memory database for each test function
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)  # Create tables
    db = SessionLocal()
    try:
        yield db  # Provide the session to the test
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Drop tables after test


def test_create_user(db):
    # Test creating a new user with valid data
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-1@"
    )

    user1 = create_user_service(request1, db)

    # Verify user is created with hashed password (not plain)
    assert user1.email == request1.email
    assert user1.hashed_password != request1.password
    assert user1.hashed_password is not None

    # Test creating a user with the same email should raise conflict error
    request2 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-1@"
    )

    with pytest.raises(HTTPException) as error:
        create_user_service(request2, db)
    assert error.value.status_code == 409  # Conflict status


def test_login_user(db):
    # Prepare user in DB
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-1@"
    )
    user1 = create_user_service(request1, db)

    # Test login with correct credentials
    logged_in_user = login_user(
        email="lolo1234@gmail.com",
        password="Test-password-1@",
        db=db
    )

    # Verify the returned user email matches and password verifies correctly
    assert logged_in_user.email == request1.email
    assert verify(request1.password, logged_in_user.hashed_password)


def test_login_user_wrong_password(db):
    # Prepare user in DB
    request1 = CreateRequest(
        email="lolo1234@gmail.com",
        password="Test-password-1@"
    )
    create_user_service(request1, db)

    # Test login with incorrect password should raise HTTPException
    with pytest.raises(HTTPException) as error:
        login_user(
            email="lolo1234@gmail.com",
            password="Wrong-password@",
            db=db
        )
    assert error.value.status_code == 401  # Unauthorized


def test_login_user_nonexistent_email(db):
    # Test login with an email not in the database should raise HTTPException
    with pytest.raises(HTTPException) as error:
        login_user(
            email="nonexistent@gmail.com",
            password="Some-password@",
            db=db
        )
    assert error.value.status_code == 401  # Unauthorized
