"""
Production-specific configuration overrides
"""
from .settings import Settings

class ProductionSettings(Settings):
    """Production environment settings"""
    
    # Production server settings
    debug: bool = False
    host: str = "0.0.0.0"  # Bind to all interfaces
    port: int = 8000
    
    # Production CORS settings - RESTRICTIVE
    cors_origins: str = "https://yourdomain.com,https://app.yourdomain.com"
    
    # Production file upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    
    # Production logging
    log_level: str = "INFO"
    
    # Security settings
    secret_key: str = None  # Must be set in production
    
    class Config:
        env_file = ".env.production"
        env_prefix = "PROD_"
        extra = "allow"  # Allow extra fields

# Create production settings instance
prod_settings = ProductionSettings()
