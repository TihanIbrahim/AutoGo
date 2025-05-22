from data_base import Base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

class Zahlung(Base):
    __tablename__ = "zahlung"

    id = Column(Integer, primary_key=True, index=True)
    vertragid = Column(Integer, ForeignKey("vertrag.id"), index=True)
    zahlungsmethode = Column(String, index=True)
    datum = Column(Date, index=True)
    status = Column(String, index=True)
    betrag = Column(Float, index=True)

    vertrag = relationship("Vertrag", back_populates="zahlungen")
