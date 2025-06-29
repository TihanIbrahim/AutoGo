from sqlalchemy import Column, Integer, Date, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from data_base import Base
from enum import Enum as pyEnum

class VertragStatus(pyEnum):
    aktiv     =  "aktiv"      # Aktiv
    beendet   =  "beendet"    # Beendet
    gekündigt =  "gekündigt"  # Gekündigt

class Vertrag(Base):
    __tablename__ = "vertrag"

    id = Column(Integer, primary_key=True, index=True)  # Vertrags-ID
    auto_id = Column(Integer, ForeignKey("auto.id"), nullable=False)  # Fahrzeug-ID
    kunden_id = Column(Integer, ForeignKey("kunden.id"), nullable=False)  # Kunden-ID
    status = Column(Enum(VertragStatus), index=True, nullable=False)  # Vertragsstatus
    beginnt_datum = Column(Date, nullable=False)  # Beginndatum
    beendet_datum = Column(Date)  # Enddatum
    total_preis = Column(Float)  # Gesamtpreis

    auto = relationship("Auto", back_populates="vertraege")  # Beziehung zum Fahrzeug
    kunde = relationship("Kunden", back_populates="vertraege")  # Beziehung zum Kunden
    zahlungen = relationship("Zahlung", back_populates="vertrag")  # Beziehung zu Zahlungen
