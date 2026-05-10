from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime

class WarningDataBase(BaseModel):
    subject: str
    date: date
    notes: Optional[str] = None
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        if not v or not v.strip():
            raise ValueError('Subject cannot be empty')
        if len(v.strip()) > 200:
            raise ValueError('Subject cannot exceed 200 characters')
        return v.strip()
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError('Warning date cannot be in the future')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v

class WarningDataCreate(WarningDataBase):
    personnel_id: int

class WarningDataUpdate(BaseModel):
    subject: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Subject cannot be empty')
            if len(v.strip()) > 200:
                raise ValueError('Subject cannot exceed 200 characters')
            return v.strip()
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Warning date cannot be in the future')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v

class WarningDataResponse(WarningDataBase):
    id: int
    personnel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
