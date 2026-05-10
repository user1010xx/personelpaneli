from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class AttendanceDataBase(BaseModel):
    month: int
    year: int
    working_days: float = 0
    leave_days: float = 0
    salary_amount: Optional[float] = None
    
    @field_validator('month')
    @classmethod
    def validate_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Month must be between 1 and 12')
        return v
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        current_year = datetime.now().year
        if not 2020 <= v <= current_year + 10:
            raise ValueError(f'Year must be between 2020 and {current_year + 10}')
        return v
    
    @field_validator('working_days')
    @classmethod
    def validate_working_days(cls, v):
        if v < 0:
            raise ValueError('Working days cannot be negative')
        if v > 31:
            raise ValueError('Working days cannot exceed 31')
        return v
    
    @field_validator('leave_days')
    @classmethod
    def validate_leave_days(cls, v):
        if v < 0:
            raise ValueError('Leave days cannot be negative')
        if v > 31:
            raise ValueError('Leave days cannot exceed 31')
        return v
    
    @field_validator('salary_amount')
    @classmethod
    def validate_salary_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Salary amount cannot be negative')
        return v

class AttendanceDataCreate(AttendanceDataBase):
    personnel_id: int

class AttendanceDataUpdate(BaseModel):
    working_days: Optional[float] = None
    leave_days: Optional[float] = None
    salary_amount: Optional[float] = None
    
    @field_validator('working_days')
    @classmethod
    def validate_working_days(cls, v):
        if v is not None and (v < 0 or v > 31):
            raise ValueError('Working days must be between 0 and 31')
        return v
    
    @field_validator('leave_days')
    @classmethod
    def validate_leave_days(cls, v):
        if v is not None and (v < 0 or v > 31):
            raise ValueError('Leave days must be between 0 and 31')
        return v
    
    @field_validator('salary_amount')
    @classmethod
    def validate_salary_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Salary amount cannot be negative')
        return v

class AttendanceDataResponse(AttendanceDataBase):
    id: int
    personnel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
