from sqlalchemy import Column, Integer, String, Float, Enum
from data_base import Base  
from sqlalchemy.orm import relationship
from enum import Enum as pyEnum

# Enum for car status values
class AutoStatus(pyEnum):
    verfügbar = "verfügbar"          # Available
    reserviert = "reserviert"        # Reserved
    vermietet = "vermietet"          # Rented
    in_wartung = "in_wartung"        # In maintenance
    beschädigt = "beschädigt"        # Damaged
    außer_betrieb = "außer_betrieb"  # Out of service

class Auto(Base):
    __tablename__ = "auto"
    
    id = Column(Integer, primary_key=True, index=True)  # Primary key for the car
    brand = Column(String, index=True, nullable=False)  # Car brand (e.g., BMW)
    model = Column(String, index=True, nullable=False)  # Car model (e.g., X5)
    jahr = Column(Integer, index=True, nullable=False)  # Manufacturing year
    preis_pro_stunde = Column(Float, index=True, nullable=False)  # Price per hour
    status = Column(Enum(AutoStatus), nullable=False) # Car availability status
    
    # Relationship to Vertrag (contract) model
    vertraege = relationship("Vertrag", back_populates="auto")
