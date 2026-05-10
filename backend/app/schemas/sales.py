from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime

class SalesDataBase(BaseModel):
    sales_count: int
    date: date
    
    @field_validator('date')
    @classmethod
    def validate_date_not_future(cls, v):
        """Date cannot be in the future"""
        if v > date.today():
            raise ValueError('Sales date cannot be in the future')
        return v
    
    @field_validator('sales_count')
    @classmethod
    def validate_sales_count(cls, v):
        """Sales count must be between 0 and 10000"""
        if v < 0:
            raise ValueError('Sales count cannot be negative')
        if v > 10000:
            raise ValueError('Sales count cannot exceed 10000')
        return v

class SalesDataCreate(SalesDataBase):
    personnel_id: int

class SalesDataUpdate(BaseModel):
    sales_count: Optional[int] = None
    
    @field_validator('sales_count')
    @classmethod
    def validate_sales_count(cls, v):
        """Sales count must be between 0 and 10000"""
        if v is not None:
            if v < 0:
                raise ValueError('Sales count cannot be negative')
            if v > 10000:
                raise ValueError('Sales count cannot exceed 10000')
        return v

class SalesDataResponse(SalesDataBase):
    id: int
    personnel_id: int
    uploaded_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SalesDataBulkUpload(BaseModel):
    """Bulk upload from Excel"""
    personnel_name: str
    date: date
    sales_count: int
    
    @field_validator('date')
    @classmethod
    def validate_date_not_future(cls, v):
        """Date cannot be in the future"""
        if v > date.today():
            raise ValueError('Sales date cannot be in the future')
        return v
    
    @field_validator('sales_count')
    @classmethod
    def validate_sales_count(cls, v):
        """Sales count must be between 0 and 10000"""
        if v < 0:
            raise ValueError('Sales count cannot be negative')
        if v > 10000:
            raise ValueError('Sales count cannot exceed 10000')
        return v
