from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class WhatsAppData(Base):
    """WhatsApp unanswered messages tracking"""
    __tablename__ = "whatsapp_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    whatsapp_count = Column(Integer, default=0)
    device_count = Column(Integer, default=0)
    average_unanswered_count = Column(Integer, default=0)
    unanswered_count = Column(Integer, default=0)
    date = Column(Date, nullable=False, index=True)
    docs_sync_date = Column(DateTime(timezone=True), nullable=True)  # Last sync from Docs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel", back_populates="whatsapp_data")
    
    # Unique: one entry per personnel per date
    # Composite index for performance
    __table_args__ = (
        UniqueConstraint('personnel_id', 'date', name='unique_personnel_whatsapp_date'),
        Index('idx_whatsapp_personnel_date', 'personnel_id', 'date'),
        CheckConstraint('whatsapp_count >= 0', name='whatsapp_count_non_negative'),
        CheckConstraint('device_count >= 0', name='whatsapp_device_count_non_negative'),
        CheckConstraint('average_unanswered_count >= 0', name='whatsapp_average_unanswered_non_negative'),
        CheckConstraint('unanswered_count >= 0', name='whatsapp_unanswered_non_negative'),
    )
