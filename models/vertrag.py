from sqlalchemy import Column, Integer, Date, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from data_base import Base
from enum import Enum as pyEnum


class VertragStatus(pyEnum):
    aktiv     =  "aktiv"      # Active
    beendet   =  "beendet"    # Ended
    gekündigt =  "gekündigt"  # Terminated

class Vertrag(Base):
    __tablename__ = "vertrag"

    id = Column(Integer, primary_key=True, index=True)  # Contract ID
    auto_id = Column(Integer, ForeignKey("auto.id"), nullable=False)  # Car ID
    kunden_id = Column(Integer, ForeignKey("kunden.id"), nullable=False)  # Customer ID
    status = Column(Enum(VertragStatus), index=True, nullable=False)  # Contract status
    beginnt_datum = Column(Date, nullable=False)  # Start date
    beendet_datum = Column(Date)  # End date
    total_preis = Column(Float)  # Total price

    auto = relationship("Auto", back_populates="vertraege")  # Car relation
    kunde = relationship("Kunden", back_populates="vertraege")  # Customer relation
    zahlungen = relationship("Zahlung", back_populates="vertrag")  # Payments relation
