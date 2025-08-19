#!/usr/bin/env python3
"""
DPQ Backend Server Startup Script
Run this to start the FastAPI server in development mode
"""

import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    print("🚀 Starting DPQ Backend Server...")
    print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print("🔄 Auto-reload enabled for development")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
