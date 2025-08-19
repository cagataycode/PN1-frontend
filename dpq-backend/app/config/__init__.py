# Configuration Package
from .settings import settings, Settings
from .development import dev_settings
from .production import prod_settings

import os

def get_settings() -> Settings:
    """
    Get the appropriate settings based on environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return prod_settings
    elif env == "development":
        return dev_settings
    else:
        return settings

# Export the active settings
active_settings = get_settings()

__all__ = [
    "settings",
    "dev_settings", 
    "prod_settings",
    "get_settings",
    "active_settings"
]
