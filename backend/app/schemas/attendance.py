from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime
import calendar

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

    @model_validator(mode='after')
    def validate_total_days(self):
        max_days = calendar.monthrange(self.year, self.month)[1]
        if self.working_days + self.leave_days > max_days:
            raise ValueError(f'Working days and leave days cannot exceed {max_days} for this month')
        return self

class AttendanceDataCreate(AttendanceDataBase):
    personnel_id: int

class AttendanceDataUpdate(BaseModel):
    month: Optional[int] = None
    year: Optional[int] = None
    working_days: Optional[float] = None
    leave_days: Optional[float] = None
    salary_amount: Optional[float] = None

    def validate_with_existing(self, existing):
        month = self.month if self.month is not None else existing.month
        year = self.year if self.year is not None else existing.year
        working_days = self.working_days if self.working_days is not None else existing.working_days
        leave_days = self.leave_days if self.leave_days is not None else existing.leave_days
        max_days = calendar.monthrange(year, month)[1]
        if working_days + leave_days > max_days:
            raise ValueError(f'Working days and leave days cannot exceed {max_days} for this month')
        return self

    @field_validator('month')
    @classmethod
    def validate_month(cls, v):
        if v is not None and not 1 <= v <= 12:
            raise ValueError('Month must be between 1 and 12')
        return v

    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v is None:
            return v
        current_year = datetime.now().year
        if not 2020 <= v <= current_year + 10:
            raise ValueError(f'Year must be between 2020 and {current_year + 10}')
        return v
    
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

    @model_validator(mode='after')
    def validate_total_days(self):
        if self.working_days is None or self.leave_days is None:
            return self
        month = self.month if self.month is not None else datetime.now().month
        year = self.year if self.year is not None else datetime.now().year
        max_days = calendar.monthrange(year, month)[1]
        if self.working_days + self.leave_days > max_days:
            raise ValueError(f'Working days and leave days cannot exceed {max_days} for this month')
        return self

class AttendanceDataResponse(AttendanceDataBase):
    id: int
    personnel_id: int
    leave_type: Optional[str] = None
    docs_sync_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
