from data_base import Base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

# This model represents a payment (Zahlung) in the database
class Zahlung(Base):
    __tablename__ = "zahlung"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for the payment
    vertragid = Column(Integer, ForeignKey("vertrag.id"), index=True)  # Reference to the related contract
    zahlungsmethode = Column(String, index=True)  # Payment method (e.g. cash, card)
    datum = Column(Date, index=True)  # Date of payment
    status = Column(String, index=True)  # Status of the payment (e.g. paid, pending)
    betrag = Column(Float, index=True)  # Amount paid

    vertrag = relationship("Vertrag", back_populates="zahlungen")  # Link to the related contract
