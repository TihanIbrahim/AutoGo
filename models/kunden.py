from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from data_base import Base  

class Kunden(Base):
    __tablename__ = "kunden"
    
    id = Column(Integer, primary_key=True, index=True)  # Primary key for the customer
    vorname = Column(String, index=True)  # Customer's first name
    nachname = Column(String, index=True)  # Customer's last name
    geb_datum = Column(Date)  # Customer's date of birth
    handy_nummer = Column(String)  # Customer's phone number
    email = Column(String, unique=True, index=True)  # Customer's email (unique)

    # Relationship with Vertrag (contract) model, cascade delete on related records
    vertraege = relationship("Vertrag", back_populates="kunde", cascade="all, delete")
