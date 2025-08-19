#!/usr/bin/env python3
"""
DPQ Backend Server Startup Script
Run this to start the FastAPI server in development mode
"""

import uvicorn
import os
from app.config import get_settings

if __name__ == "__main__":
    # Get the appropriate settings based on environment
    settings = get_settings()
    
    print("🚀 Starting DPQ Backend Server...")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if settings.debug else 'disabled'}")
    print(f"🐛 Debug mode: {'enabled' if settings.debug else 'disabled'}")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=getattr(settings, 'log_level', 'info').lower()
    )
