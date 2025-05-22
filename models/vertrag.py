from sqlalchemy import Column, Integer, Date, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from data_base import Base

class Vertrag(Base):
    __tablename__ = "vertrag"

    id = Column(Integer, primary_key=True, index=True)
    auto_id = Column(Integer, ForeignKey("auto.id"))
    kunden_id = Column(Integer, ForeignKey("kunden.id"))
    status = Column(Boolean)
    beginnt_datum = Column(Date)
    beendet_datum = Column(Date)
    total_preis = Column(Float)

    auto = relationship("Auto", back_populates="vertraege")
    kunde = relationship("Kunden", back_populates="vertraege")
    zahlungen = relationship("Zahlung", back_populates="vertrag")
