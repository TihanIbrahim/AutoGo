from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from data_base import Base  

class Kunden(Base):
    __tablename__ = "kunden"
    
    id = Column(Integer, primary_key=True, index=True)  # Primärschlüssel für den Kunden
    vorname = Column(String(50), index=True, nullable=False)  # Vorname des Kunden
    nachname = Column(String(50), index=True, nullable=False)  # Nachname des Kunden
    geb_datum = Column(Date)  # Geburtsdatum des Kunden
    handy_nummer = Column(String(20), nullable=True)  # Telefonnummer des Kunden
    email = Column(String, unique=True, index=True, nullable=False)  # E-Mail des Kunden (eindeutig)

    # Beziehung zum Vertrag-Modell, Cascade-Löschung der zugehörigen Einträge
    vertraege = relationship("Vertrag", back_populates="kunde", cascade="all, delete")
