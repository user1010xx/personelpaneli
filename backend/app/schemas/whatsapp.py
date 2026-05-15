from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime

class WhatsAppDataBase(BaseModel):
    whatsapp_count: int = 0
    device_count: int = 0
    average_unanswered_count: int = 0
    unanswered_count: int = 0
    date: date

    @field_validator('whatsapp_count', 'device_count', 'average_unanswered_count')
    @classmethod
    def validate_non_negative_fields(cls, v):
        if v < 0:
            raise ValueError('Count fields cannot be negative')
        return v

    @field_validator('unanswered_count')
    @classmethod
    def validate_unanswered_count(cls, v):
        if v < 0:
            raise ValueError('Unanswered count cannot be negative')
        return v

class WhatsAppDataCreate(WhatsAppDataBase):
    personnel_id: int

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError('WhatsApp record date cannot be in the future')
        return v

class WhatsAppDataUpdate(BaseModel):
    whatsapp_count: Optional[int] = None
    device_count: Optional[int] = None
    average_unanswered_count: Optional[int] = None
    unanswered_count: Optional[int] = None

    @field_validator('whatsapp_count', 'device_count', 'average_unanswered_count')
    @classmethod
    def validate_non_negative_fields(cls, v):
        if v is not None and v < 0:
            raise ValueError('Count fields cannot be negative')
        return v

    @field_validator('unanswered_count')
    @classmethod
    def validate_unanswered_count(cls, v):
        if v is not None and v < 0:
            raise ValueError('Unanswered count cannot be negative')
        return v

class WhatsAppDataResponse(WhatsAppDataBase):
    id: int
    personnel_id: int
    docs_sync_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
