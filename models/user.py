from sqlalchemy import Column, String, Integer
from data_base import Base

# User model representing users table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # User ID
    email = Column(String(255), unique=True, index=True, nullable=False)   # User email
    hashed_password = Column(String(128), nullable=False)                  # Password hash
    role = Column(String(50), default="owner", nullable=False)          # User role
