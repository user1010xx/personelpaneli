from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Float, UniqueConstraint, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class SalesData(Base):
    """Sales data model - daily sales per personnel"""
    __tablename__ = "sales_data"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    sales_count = Column(Integer, nullable=False, default=0)
    date = Column(Date, nullable=False, index=True)  # Date of sales
    uploaded_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel", back_populates="sales_data")
    
    # Unique constraint: one entry per personnel per date
    # Check constraint: sales_count must be 0-10000
    __table_args__ = (
        UniqueConstraint('personnel_id', 'date', name='unique_personnel_sales_date'),
        CheckConstraint('sales_count >= 0 AND sales_count <= 10000', name='sales_count_range'),
    )
