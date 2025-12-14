"""
Configuration management using environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # App Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    
    # AWS S3 (Surfside)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    
    # Vibe API
    VIBE_API_BASE_URL: str = "https://api.vibe.co"
    VIBE_API_KEY: Optional[str] = None
    VIBE_ADVERTISER_ID: Optional[str] = None
    VIBE_RATE_LIMIT_PER_HOUR: int = 15
    
    # Email (SMTP)
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Dashboard Alerts"
    
    # File Upload
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB in bytes
    
    # Scheduler
    SURFSIDE_CRON_HOUR: int = 5
    VIBE_CRON_HOUR: int = 6
    AGGREGATION_CRON_HOUR: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
