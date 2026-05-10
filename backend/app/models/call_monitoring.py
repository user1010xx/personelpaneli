from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Float, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class CallMonitoring(Base):
    """Call Monitoring/Dinlenen Çağrılar model"""
    __tablename__ = "call_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    phone_number = Column(String, nullable=False)
    quality_score = Column(Float, nullable=False)  # 0-100 scale
    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel")
    
    # Composite index for performance
    __table_args__ = (
        Index('idx_call_monitoring_personnel_date', 'personnel_id', 'date'),
    )
