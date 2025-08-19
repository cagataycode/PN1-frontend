"""
Development-specific configuration overrides
"""
from .settings import Settings

class DevelopmentSettings(Settings):
    """Development environment settings"""
    
    # Override default settings for development
    debug: bool = True
    host: str = "127.0.0.1"  # Localhost only for development
    port: int = 8000
    
    # Development CORS settings
    cors_origins: str = "*"  # Allow all for development
    
    # Development file upload settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB for development
    upload_dir: str = "uploads_dev"
    
    # Development logging
    log_level: str = "DEBUG"
    
    class Config:
        env_file = ".env.development"
        env_prefix = "DEV_"
        extra = "allow"  # Allow extra fields

# Create development settings instance
dev_settings = DevelopmentSettings()
