from datetime import datetime

from pydantic import BaseModel, field_validator


class DocsLinkBase(BaseModel):
    key: str
    label: str
    url: str

    @field_validator("key")
    @classmethod
    def validate_key(cls, value):
        allowed = {"personnel", "attendance", "warnings", "whatsapp"}
        cleaned = (value or "").strip().lower()
        if cleaned not in allowed:
            raise ValueError("Invalid docs link key")
        return cleaned

    @field_validator("label", "url")
    @classmethod
    def validate_text(cls, value):
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        return cleaned


class DocsLinkUpdate(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError("URL cannot be empty")
        return cleaned


class DocsLinkResponse(BaseModel):
    id: int
    key: str
    label: str
    url: str
    spreadsheet_id: str
    gid: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True