from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import date, time, datetime

class TrainingDataBase(BaseModel):
    subject: str
    date: date
    start_time: time
    end_time: time
    trainer: Optional[str] = None
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
        today = date.today()
        if v > today:
            raise ValueError('Training date cannot be in the future')
        if (today - v).days > 365 * 2:  # 2 years ago
            raise ValueError('Training date cannot be more than 2 years in the past')
        return v
    
    @field_validator('trainer')
    @classmethod
    def validate_trainer(cls, v):
        if v is not None and len(v.strip()) > 100:
            raise ValueError('Trainer name cannot exceed 100 characters')
        return v.strip() if v else v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v
    
    @model_validator(mode='after')
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError('Start time must be before end time')
        return self

class TrainingDataCreate(TrainingDataBase):
    personnel_id: int

class TrainingDataUpdate(BaseModel):
    subject: Optional[str] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    trainer: Optional[str] = None
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
        if v is not None:
            today = date.today()
            if v > today:
                raise ValueError('Training date cannot be in the future')
            if (today - v).days > 365 * 2:  # 2 years ago
                raise ValueError('Training date cannot be more than 2 years in the past')
        return v
    
    @field_validator('trainer')
    @classmethod
    def validate_trainer(cls, v):
        if v is not None and len(v.strip()) > 100:
            raise ValueError('Trainer name cannot exceed 100 characters')
        return v.strip() if v else v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v
    
    @model_validator(mode='after')
    def validate_times(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError('Start time must be before end time')
        return self

class TrainingDataResponse(TrainingDataBase):
    id: int
    personnel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
