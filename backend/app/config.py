from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/personelpanel"

    # JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INITIAL_ADMIN_USERNAME: str = ""
    INITIAL_ADMIN_EMAIL: str = ""
    INITIAL_ADMIN_PASSWORD: str = ""
    INITIAL_ADMIN_FULL_NAME: str = "Administrator"

    # API
    API_TITLE: str = "Personel Panel API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool | str = False

    RATE_LIMIT_ENABLED: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Docs Links
    PERSONNEL_SHEET_ID: str = ""
    DOCS_PUANTAJ_ID: str = ""
    DOCS_UYARILAR_ID: str = ""
    WARNINGS_SHEET_ID: str = ""
    DOCS_WHATSAPP_ID: str = ""
    DEFAULT_PERSONNEL_SHEET_URL: str = ""
    DEFAULT_ATTENDANCE_SHEET_URL: str = ""
    DEFAULT_WARNINGS_SHEET_URL: str = ""
    DEFAULT_WHATSAPP_SHEET_URL: str = ""

    # Google Docs API
    GOOGLE_CREDENTIALS_PATH: str = "./credentials.json"
    GOOGLE_CREDENTIALS_JSON: str = ""

    @field_validator('DEBUG')
    @classmethod
    def validate_debug(cls, v):
        if isinstance(v, bool):
            return v
        value = str(v).strip().lower()
        if value in {"1", "true", "yes", "on", "debug", "development", "dev"}:
            return True
        if value in {"0", "false", "no", "off", "release", "production", "prod"}:
            return False
        return False

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY environment variable must be set (min 32 characters)")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }

settings = Settings()
