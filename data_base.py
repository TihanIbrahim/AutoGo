import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get the database URL from environment variable or use default if not set
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:123456789@localhost/DB1")

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency function to get a database session
def get_database_session():
    db = SessionLocal()
    try:
        yield db  # provide the session
    finally:
        db.close()  # close the session after use
