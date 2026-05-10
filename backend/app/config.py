from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/personelpanel")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set (min 32 characters)")
    
    # API
    API_TITLE: str = "Personel Panel API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://localhost:8000"
        ).split(",")
    ]
    
    # Docs Links (to be added)
    DOCS_PUANTAJ_ID: str = os.getenv("DOCS_PUANTAJ_ID", "")
    DOCS_UYARILAR_ID: str = os.getenv("DOCS_UYARILAR_ID", "")
    DOCS_WHATSAPP_ID: str = os.getenv("DOCS_WHATSAPP_ID", "")
    
    # Google Docs API
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
