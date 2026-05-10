from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class WhatsAppData(Base):
    """WhatsApp unanswered messages tracking"""
    __tablename__ = "whatsapp_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    unanswered_count = Column(Integer, default=0)
    date = Column(Date, nullable=False, index=True)
    docs_sync_date = Column(DateTime(timezone=True), nullable=True)  # Last sync from Docs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel")
    
    # Unique: one entry per personnel per date
    # Composite index for performance
    __table_args__ = (
        UniqueConstraint('personnel_id', 'date', name='unique_personnel_whatsapp_date'),
        Index('idx_whatsapp_personnel_date', 'personnel_id', 'date'),
    )
