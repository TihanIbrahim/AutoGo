from sqlalchemy import Column, Integer, String, Float, Enum
from data_base import Base  
from sqlalchemy.orm import relationship
from enum import Enum as pyEnum

# Enum für Fahrzeugstatuswerte
class AutoStatus(pyEnum):
    verfügbar = "verfügbar"          # Verfügbar (Verfügbar)
    reserviert = "reserviert"        # Reserviert (Reserviert)
    vermietet = "vermietet"          # Vermietet (Vermietet)
    in_wartung = "in_wartung"        # In Wartung (In Wartung)
    beschädigt = "beschädigt"        # Beschädigt (Beschädigt)
    außer_betrieb = "außer_betrieb"  # Außer Betrieb (Außer Betrieb)

class Auto(Base):
    __tablename__ = "auto"
    
    id = Column(Integer, primary_key=True, index=True)  # Primärschlüssel für das Fahrzeug
    brand = Column(String, index=True, nullable=False)  # Automarke (z.B. BMW)
    model = Column(String, index=True, nullable=False)  # Automodell (z.B. X5)
    jahr = Column(Integer, index=True, nullable=False)  # Herstellungsjahr
    preis_pro_stunde = Column(Float, index=True, nullable=False)  # Preis pro Stunde
    status = Column(Enum(AutoStatus), nullable=False)  # Fahrzeugstatus
    
    # Beziehung zum Vertrag-Modell
    vertraege = relationship("Vertrag", back_populates="auto")
