from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Personnel(Base):
    """Personnel/Employee model"""
    __tablename__ = "personnel"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    hire_date = Column(Date, nullable=True)
    reference = Column(String, nullable=True)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    promotion_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with cascade delete
    sales_data = relationship("SalesData", back_populates="personnel", cascade="all, delete-orphan")
    attendance_data = relationship("AttendanceData", back_populates="personnel", cascade="all, delete-orphan")
    warning_data = relationship("WarningData", back_populates="personnel", cascade="all, delete-orphan")
    training_data = relationship("TrainingData", back_populates="personnel", cascade="all, delete-orphan")
    call_monitoring = relationship("CallMonitoring", back_populates="personnel", cascade="all, delete-orphan")
    whatsapp_data = relationship("WhatsAppData", back_populates="personnel", cascade="all, delete-orphan")
    call_process_data = relationship("CallProcessData", back_populates="personnel", cascade="all, delete-orphan")
