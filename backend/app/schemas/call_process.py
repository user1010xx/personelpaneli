from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CallProcessDataBase(BaseModel):
    call_count: int
    talk_duration: float
    average_ring_duration: float
    date: date

    @field_validator("date")
    @classmethod
    def validate_date_not_future(cls, value):
        if value > date.today():
            raise ValueError("Call process date cannot be in the future")
        return value

    @field_validator("call_count")
    @classmethod
    def validate_call_count(cls, value):
        if value < 0:
            raise ValueError("Call count cannot be negative")
        return value

    @field_validator("talk_duration", "average_ring_duration")
    @classmethod
    def validate_durations(cls, value):
        if value < 0:
            raise ValueError("Duration cannot be negative")
        return value


class CallProcessDataCreate(CallProcessDataBase):
    personnel_id: int


class CallProcessDataUpdate(BaseModel):
    call_count: Optional[int] = None
    talk_duration: Optional[float] = None
    average_ring_duration: Optional[float] = None

    @field_validator("call_count")
    @classmethod
    def validate_call_count(cls, value):
        if value is not None and value < 0:
            raise ValueError("Call count cannot be negative")
        return value

    @field_validator("talk_duration", "average_ring_duration")
    @classmethod
    def validate_durations(cls, value):
        if value is not None and value < 0:
            raise ValueError("Duration cannot be negative")
        return value


class CallProcessDataResponse(CallProcessDataBase):
    id: int
    personnel_id: int
    uploaded_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CallProcessDataBulkUpload(BaseModel):
    personnel_name: str
    date: date
    call_count: int
    talk_duration: float
    average_ring_duration: float

    @field_validator("date")
    @classmethod
    def validate_date_not_future(cls, value):
        if value > date.today():
            raise ValueError("Call process date cannot be in the future")
        return value