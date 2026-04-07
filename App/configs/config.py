"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FL-DP Healthcare CKD Prediction"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = "sqlite:///./App/database/app.db"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    
    # File Upload
    UPLOAD_DIR: str = "./App/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # ML Model Paths
    TEMPLATE_CSV: str = "./FL-DP-Healthcare/data/chronic_kidney_disease_5000.csv"
    SERVER_DIR: str = "./FL-DP-Healthcare/server"
    CLIENTS_BASE_DIR: str = "./FL-DP-Healthcare"
    
    # Training defaults
    DEFAULT_EPOCHS: int = 30
    DEFAULT_BATCH_SIZE: int = 64
    DEFAULT_LEARNING_RATE: float = 0.001
    DEFAULT_LOCAL_EPOCHS: int = 10
    DEFAULT_MAX_GRAD_NORM: float = 1.0
    DEFAULT_NOISE_MULTIPLIER: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Made with Bob
