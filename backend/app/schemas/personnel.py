from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date
import re

class PersonnelBase(BaseModel):
    name: str
    employee_id: str
    username: Optional[str] = None
    hire_date: Optional[date] = None
    reference: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    promotion_date: Optional[date] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 100:
            raise ValueError('Name cannot exceed 100 characters')
        return v.strip()

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Employee ID cannot be empty')
        value = v.strip()
        if len(value) > 255:
            raise ValueError('Employee ID cannot exceed 255 characters')
        return value

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            value = v.strip()
            if not value:
                return None
            if len(value) > 255:
                raise ValueError('Username cannot exceed 255 characters')
            return value
        return v

    @field_validator('reference')
    @classmethod
    def validate_reference(cls, v):
        if v is not None:
            value = v.strip()
            if len(value) > 255:
                raise ValueError('Reference cannot exceed 255 characters')
            return value or None
        return v

    @field_validator('department', 'position')
    @classmethod
    def validate_optional_text(cls, v):
        if v is not None:
            value = v.strip()
            if len(value) > 100:
                raise ValueError('Field cannot exceed 100 characters')
            return value or None
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            value = v.strip()
            if not value:
                return None
            cleaned = re.sub(r'[^\d]', '', value)
            if not re.match(r'^(90|0)?5[0-9]{9}$', cleaned):
                raise ValueError('Invalid Turkish phone number format')
            return value
        return v

class PersonnelCreate(PersonnelBase):
    pass

class PersonnelUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    hire_date: Optional[date] = None
    reference: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    promotion_date: Optional[date] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Name cannot be empty')
            if len(v.strip()) > 100:
                raise ValueError('Name cannot exceed 100 characters')
            return v.strip()
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            value = v.strip()
            if not value:
                return None
            if len(value) > 255:
                raise ValueError('Username cannot exceed 255 characters')
            return value
        return v

    @field_validator('reference')
    @classmethod
    def validate_reference(cls, v):
        if v is not None:
            value = v.strip()
            if len(value) > 255:
                raise ValueError('Reference cannot exceed 255 characters')
            return value or None
        return v

    @field_validator('department', 'position')
    @classmethod
    def validate_optional_text(cls, v):
        if v is not None:
            value = v.strip()
            if len(value) > 100:
                raise ValueError('Field cannot exceed 100 characters')
            return value or None
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            value = v.strip()
            if not value:
                return None
            cleaned = re.sub(r'[^\d]', '', value)
            if not re.match(r'^(90|0)?5[0-9]{9}$', cleaned):
                raise ValueError('Invalid Turkish phone number format')
            return value
        return v

class PersonnelResponse(PersonnelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True