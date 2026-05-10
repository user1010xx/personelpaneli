from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonnelBase(BaseModel):
    name: str
    employee_id: str
    department: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class PersonnelCreate(PersonnelBase):
    pass

class PersonnelUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class PersonnelResponse(PersonnelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
