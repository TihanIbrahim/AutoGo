from sqlalchemy import Column, Integer, String, Boolean
from data_base import Base  
from sqlalchemy.orm import relationship

class Auto(Base):
    __tablename__ = "auto"
    
    id = Column(Integer, primary_key=True, index=True)  # Primary key for the car
    brand = Column(String, index=True)  # Car brand
    model = Column(String, index=True)  # Car model
    jahr = Column(Integer, index=True)  # Car year
    preis_pro_stunde = Column(Integer, index=True)  # Price per hour
    status = Column(Boolean, index=True)  # Car availability status
    
    # Relationship to Vertrag (contract) model
    vertraege = relationship("Vertrag", back_populates="auto")




    
