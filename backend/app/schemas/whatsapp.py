from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class WhatsAppDataBase(BaseModel):
    unanswered_count: int = 0
    date: date

class WhatsAppDataCreate(WhatsAppDataBase):
    personnel_id: int

class WhatsAppDataUpdate(BaseModel):
    unanswered_count: Optional[int] = None

class WhatsAppDataResponse(WhatsAppDataBase):
    id: int
    personnel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
