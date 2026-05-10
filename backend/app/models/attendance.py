from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Float, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class AttendanceData(Base):
    """Attendance/Puantaj data model"""
    __tablename__ = "attendance_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    working_days = Column(Float, default=0)  # 28.5 örnek
    leave_days = Column(Float, default=0)  # 1.5 örnek
    leave_type = Column(String, nullable=True)  # full_day, half_day, etc.
    salary_amount = Column(Float, nullable=True)  # Monthly salary
    docs_sync_date = Column(DateTime(timezone=True), nullable=True)  # Last sync from Docs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel")
    
    # Unique: one entry per personnel per month/year
    # Composite index for performance
    __table_args__ = (
        UniqueConstraint('personnel_id', 'month', 'year', name='unique_personnel_month_year'),
        Index('idx_personnel_month_year', 'personnel_id', 'month', 'year'),
    )
