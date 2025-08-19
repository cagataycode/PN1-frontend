import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "DPQ Backend API"
    api_version: str = "1.0.0"
    api_description: str = "Dog Personality Quiz Backend Server"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: list = ["*"]  # In production, restrict this
    
    # Database Configuration (Supabase)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # Claude API Configuration
    anthropic_api_key: Optional[str] = None
    
    # Security Configuration
    secret_key: Optional[str] = None
    
    # File Upload Configuration
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate that required settings are present"""
    required_settings = [
        "supabase_url",
        "supabase_key", 
        "anthropic_api_key"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")

# Load and validate settings on import
try:
    validate_settings()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
