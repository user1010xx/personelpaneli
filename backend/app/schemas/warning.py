from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime

class WarningDataBase(BaseModel):
    deduction: Optional[str] = None
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
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v

    @field_validator('deduction')
    @classmethod
    def validate_deduction(cls, v):
        if v is not None:
            value = v.strip()
            if len(value) > 100:
                raise ValueError('Deduction cannot exceed 100 characters')
            return value or None
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
