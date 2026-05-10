from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Personnel(Base):
    """Personnel/Employee model"""
    __tablename__ = "personnel"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
