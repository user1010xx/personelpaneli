from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date as DateType, datetime
import re

class CallMonitoringBase(BaseModel):
    phone_number: str
    quality_score: float
    date: DateType
    notes: Optional[str] = None
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Phone number cannot be empty')
        value = v.strip()
        cleaned = re.sub(r'[^\d]', '', value)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError('Phone number must contain between 10 and 15 digits')
        return value
    
    @field_validator('quality_score')
    @classmethod
    def validate_quality_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Quality score must be between 0 and 100')
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v > DateType.today():
            raise ValueError('Call monitoring date cannot be in the future')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v

class CallMonitoringCreate(CallMonitoringBase):
    personnel_id: int

class CallMonitoringUpdate(BaseModel):
    phone_number: Optional[str] = None
    quality_score: Optional[float] = None
    date: Optional[DateType] = None
    notes: Optional[str] = None
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None:
            value = v.strip()
            if not value:
                raise ValueError('Phone number cannot be empty')
            cleaned = re.sub(r'[^\d]', '', value)
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError('Phone number must contain between 10 and 15 digits')
            return value
        return v
    
    @field_validator('quality_score')
    @classmethod
    def validate_quality_score(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Quality score must be between 0 and 100')
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v is not None and v > DateType.today():
            raise ValueError('Call monitoring date cannot be in the future')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v

class CallMonitoringResponse(CallMonitoringBase):
    id: int
    personnel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
