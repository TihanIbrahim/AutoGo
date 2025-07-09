from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum
from data_base import Base
from sqlalchemy.orm import relationship
from enum import Enum as pyEnum

# Aufzählung der Zahlungsmethoden, definiert mögliche Zahlungsarten wie Karte, Überweisung, PayPal, Stripe und Klarna
class ZahlungsmethodeEnum(pyEnum):
    karte = "karte"
    überweisung = "überweisung"
    paypal = "PAYPAL"
    stripe = "stripe"
    klarna = "Klarna"

# Aufzählung des Zahlungsstatus, repräsentiert verschiedene Zahlungszustände wie bezahlt, offen, abgebrochen, teilweise und zurückerstattet
class ZahlungsStatusEnum(pyEnum):
    bezahlt = "bezahlt"
    offen = "offen"
    abgebrochen = "abgebrochen"
    teilweise = "teilweise"
    zurückerstattet = "zurückerstattet"

class Zahlung(Base):
    __tablename__ = "zahlung"  # Tabellenname in der Datenbank

    id = Column(Integer, primary_key=True, index=True)  # Eindeutige ID für die Zahlung
    vertrag_id = Column(Integer, ForeignKey("vertrag.id"), index=True, nullable=False)  # Referenz zum zugehörigen Vertrag
    zahlungsmethode = Column(Enum(ZahlungsmethodeEnum), index=True, nullable=False)  # Zahlungsmethode (z.B. Karte, Überweisung)
    datum = Column(Date, index=True, nullable=False)  # Zahlungsdatum
    status = Column(Enum(ZahlungsStatusEnum), index=True, nullable=False)  # Zahlungsstatus (z.B. bezahlt, offen)
    betrag = Column(Float, index=True, nullable=False)  # Bezahlt Betrag

    vertrag = relationship("Vertrag", back_populates="zahlungen")  # Verbindung zum zugehörigen Vertrag
