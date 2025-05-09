from sqlalchemy import Column, Integer, String, Boolean
from data_base import Base  
from sqlalchemy.orm import relationship

class Auto(Base):
    __tablename__ = "auto"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    jahr = Column(Integer, index=True)
    preis_pro_stunde = Column(Integer, index=True)
    status = Column(Boolean, index=True)

    vertraege = relationship("Vertrag", back_populates="auto")
