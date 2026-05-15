from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, Float, UniqueConstraint, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class CallProcessData(Base):
    __tablename__ = "call_process_data"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True)
    call_count = Column(Integer, nullable=False, default=0)
    talk_duration = Column(Float, nullable=False, default=0)
    average_ring_duration = Column(Float, nullable=False, default=0)
    date = Column(Date, nullable=False, index=True)
    uploaded_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    personnel = relationship("Personnel", back_populates="call_process_data")

    __table_args__ = (
        UniqueConstraint("personnel_id", "date", name="unique_personnel_call_process_date"),
        CheckConstraint("call_count >= 0", name="call_process_count_non_negative"),
        CheckConstraint("talk_duration >= 0", name="call_process_talk_non_negative"),
        CheckConstraint("average_ring_duration >= 0", name="call_process_ring_non_negative"),
    )