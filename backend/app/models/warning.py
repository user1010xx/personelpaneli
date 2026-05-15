from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class WarningData(Base):
    """Warnings/Uyari Kesinti model - from Google Sheets"""
    __tablename__ = "warning_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    deduction = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    docs_id = Column(String, nullable=True)
    docs_sync_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    personnel = relationship("Personnel", back_populates="warning_data")
    
    __table_args__ = (
        Index('idx_warning_personnel_date', 'personnel_id', 'date'),
    )