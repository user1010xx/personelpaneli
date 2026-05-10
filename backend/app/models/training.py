from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Time, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class TrainingData(Base):
    """Training/Eğitim data model - manually entered"""
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, nullable=False)  # Eğitim konusu
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    trainer = Column(String, nullable=True)  # Eğitmen adı
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel")
    
    # Composite index for performance
    __table_args__ = (
        Index('idx_training_personnel_date', 'personnel_id', 'date'),
    )
