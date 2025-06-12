from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from data_base import Base
from sqlalchemy.orm import relationship
from enum import Enum as pyEnum


# Payment method enumeration defining possible payment types such as card, bank transfer, PayPal, Stripe, and Klarna. 
class ZahlungsmethodeEnum(pyEnum):
    karte = "karte"
    überweisung = "überweisung"
    paypal = "PAYPAL"
    stripe = "stripe"
    klarna = "Klarna"

# Payment status enumeration representing different states of a payment like paid, open, cancelled, partial, and refunded.
class ZahlungsStatusEnum(pyEnum):
    bezahlt = "bezahlt"
    offen = "offen"
    abgebrochen = "abgebrochen"
    teilweise = "teilweise"
    zurückerstattet = "zurückerstattet"


class Zahlung(Base):
    __tablename__ = "zahlung"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for the payment
    vertrag_id = Column(Integer, ForeignKey("vertrag.id"), index=True, nullable=False)  # Reference to the related contract
    zahlungsmethode = Column(Enum(ZahlungsmethodeEnum), index=True, nullable=False)  # Payment method (e.g. cash, card)
    datum = Column(Date, index=True, nullable=False)  # Date of payment
    status = Column(Enum(ZahlungsStatusEnum), index=True , nullable=False)  # Status of the payment (e.g. paid, pending)
    betrag = Column(Float, index=True,nullable=False)  # Amount paid

    vertrag = relationship("Vertrag", back_populates="zahlungen")  # Link to the related contract