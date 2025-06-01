from sqlalchemy import Column, Integer, Date, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from data_base import Base

# This model represents a rental contract (Vertrag) in the database
class Vertrag(Base):
    __tablename__ = "vertrag"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for the contract
    auto_id = Column(Integer, ForeignKey("auto.id"))  # Reference to the rented car
    kunden_id = Column(Integer, ForeignKey("kunden.id"))  # Reference to the customer
    status = Column(Boolean)  # Contract status (active or cancelled)
    beginnt_datum = Column(Date)  # Start date of the contract
    beendet_datum = Column(Date)  # End date of the contract
    total_preis = Column(Float)  # Total price for the rental period

    auto = relationship("Auto", back_populates="vertraege")  # Link to the car model
    kunde = relationship("Kunden", back_populates="vertraege")  # Link to the customer model
    zahlungen = relationship("Zahlung", back_populates="vertrag")  # All payments for this contract
