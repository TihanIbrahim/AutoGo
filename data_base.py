import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Hole die Datenbank-URL aus der Umgebungsvariable oder verwende den Standardwert
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:123456789@localhost/DB1")

# Erstelle den Datenbank-Engine (Verbindung zur DB)
engine = create_engine(DATABASE_URL)

# Erstelle eine konfigurierte Session-Klasse für DB-Sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basisklasse für ORM-Modelle
Base = declarative_base()

# Dependency-Funktion, die eine DB-Session liefert und nach Nutzung schließt
def get_database_session():
    db = SessionLocal()
    try:
        yield db  # gibt die Session zurück
    finally:
        db.close()  # schließt die Session danach
