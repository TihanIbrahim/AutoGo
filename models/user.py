from sqlalchemy import Column, String, Integer
from data_base import Base

# User-Modell, das die Tabelle "users" repräsentiert
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Benutzer-ID
    email = Column(String(255), unique=True, index=True, nullable=False)   # Benutzer-E-Mail
    hashed_password = Column(String(128), nullable=False)                  # Passwort-Hash
    role = Column(String(50), default="customer", nullable=False)          # Benutzerrolle
