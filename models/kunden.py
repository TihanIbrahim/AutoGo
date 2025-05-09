from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from data_base import Base  

class Kunden(Base):
    __tablename__ = "kunden"
    
    id = Column(Integer, primary_key=True, index=True)
    vorname = Column(String, index=True)
    nachname = Column(String, index=True)
    geb_datum = Column(Date)
    handy_nummer = Column(String)
    email = Column(String, unique=True, index=True)

    vertraege = relationship("Vertrag", back_populates="kunde", cascade="all, delete")