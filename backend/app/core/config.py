"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "QuickBooks Commerce Forecasting"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # ML Model
    MODEL_PATH: str = "data/models"
    MODEL_VERSION: str = "v1.0"
    
    # Data
    DATA_PATH: str = "data"
    CACHE_TTL: int = 3600  # 1 hour
    
    # External APIs
    FRED_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_KEY: Optional[str] = None
    
    # Redis (optional for caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
