"""
Configuration management using environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # App Settings
    SECRET_KEY: str
    ENCRYPTION_KEY: str  # Fernet key for encrypting sensitive data (API keys, etc.)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days (60 * 24 * 8)
    DEBUG: bool = False
    
    # CORS Configuration - Read from environment variable or .env file
    # Example: CORS_ORIGINS='["https://your-app.vercel.app","http://localhost:3000"]'
    # Default for development (will be overridden by docker-compose.yml in production)
    CORS_ORIGINS: str = '["http://localhost:3000"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list. REQUIRES environment variable configuration."""
        try:
            # Debug: Print what we're trying to parse
            print(f"[DEBUG] CORS_ORIGINS raw value: {repr(self.CORS_ORIGINS)}")
            origins = json.loads(self.CORS_ORIGINS)
            if not origins:
                raise ValueError("CORS_ORIGINS cannot be empty")
            print(f"[DEBUG] Parsed CORS origins: {origins}")
            return origins
        except json.JSONDecodeError as e:
            raise ValueError(
                f"CORS_ORIGINS must be valid JSON array. "
                f"Received: {repr(self.CORS_ORIGINS)}. "
                f"JSON Error: {e}"
            )
        except Exception as e:
            raise ValueError(
                f"CORS_ORIGINS parsing failed. "
                f"Value: {repr(self.CORS_ORIGINS)}. "
                f"Error: {type(e).__name__}: {e}"
            )
    
    # AWS S3 (Surfside)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    
    # Vibe API
    VIBE_API_BASE_URL: str = "https://clear-platform.vibe.co"
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
    
    # Scheduler (all times in Eastern Time per documentation)
    DAILY_INGESTION_HOUR: int = 3      # 3:30 AM Eastern (documentation: 3-4 AM)
    DAILY_INGESTION_MINUTE: int = 30
    WEEKLY_AGGREGATION_HOUR: int = 5   # Monday 5:00 AM Eastern
    MONTHLY_AGGREGATION_HOUR: int = 5  # 1st of month 5:00 AM Eastern
    
    class Config:
        env_file = ".env"  # Will be ignored if file doesn't exist (Docker)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"
        # Environment variables take precedence over .env file


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
