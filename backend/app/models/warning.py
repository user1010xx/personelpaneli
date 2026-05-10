from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class WarningData(Base):
    """Warnings/Uyarılar model - from Docs"""
    __tablename__ = "warning_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, nullable=False)  # Uyarı konusu
    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    docs_id = Column(String, nullable=True)  # Document ID from Docs
    docs_sync_date = Column(DateTime(timezone=True), nullable=True)  # Last sync from Docs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel")
    
    # Composite index for performance
    __table_args__ = (
        Index('idx_warning_personnel_date', 'personnel_id', 'date'),
    )
