from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
import sys
import os
from datetime import datetime
from contextlib import asynccontextmanager
from app.config import active_settings, get_settings

# Configure logging based on environment
def setup_logging():
    """Setup logging configuration based on environment settings"""
    log_level = getattr(active_settings, 'log_level', 'INFO').upper()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for production
    if not active_settings.debug:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/dpq_backend.log")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting DPQ Backend Server...")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🐛 Debug mode: {active_settings.debug}")
    logger.info(f"🌐 Host: {active_settings.host}:{active_settings.port}")
    logger.info(f"🔒 CORS origins: {active_settings.cors_origins}")
    logger.info("✅ Server startup completed")
    yield
    # Shutdown
    logger.info("🛑 Shutting down DPQ Backend Server...")
    logger.info("✅ Server shutdown completed")

# Create FastAPI app
app = FastAPI(
    title=active_settings.api_title,
    description=active_settings.api_description,
    version=active_settings.api_version,
    lifespan=lifespan,
    debug=active_settings.debug
)

# Configure CORS for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=active_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "DPQ Backend API is running",
        "service": active_settings.api_title,
        "version": active_settings.api_version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    logger.debug("Health check endpoint accessed")
    
    # Check system health
    health_status = {
        "status": "healthy",
        "service": active_settings.api_title,
        "version": active_settings.api_version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running",  # Could calculate actual uptime later
        "debug": active_settings.debug,
        "cors_origins": len(active_settings.cors_origins_list),
        "checks": {
            "api": "healthy",
            "config": "loaded",
            "logging": "configured"
        }
    }
    
    return health_status

@app.get("/api/health")
async def api_health_check():
    """API-specific health check endpoint"""
    logger.debug("API health check endpoint accessed")
    return {
        "status": "healthy",
        "api": active_settings.api_title,
        "version": active_settings.api_version,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_health": "/api/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    logger.debug("API info endpoint accessed")
    return {
        "service": active_settings.api_title,
        "description": active_settings.api_description,
        "version": active_settings.api_version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": active_settings.debug,
        "configuration": {
            "cors_origins": active_settings.cors_origins,
            "max_file_size": f"{active_settings.max_file_size / (1024*1024):.1f} MB",
            "upload_directory": active_settings.upload_dir
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=active_settings.host,
        port=active_settings.port,
        reload=active_settings.debug,
        log_level=active_settings.log_level.lower() if hasattr(active_settings, 'log_level') else "info"
    )
