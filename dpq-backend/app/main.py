from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
from app.config import active_settings, get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting DPQ Backend Server...")
    yield
    # Shutdown
    logger.info("Shutting down DPQ Backend Server...")

# Create FastAPI app
app = FastAPI(
    title="DPQ Backend API",
    description="Dog Personality Quiz Backend Server",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=active_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DPQ Backend API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DPQ Backend",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api": "DPQ Backend API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=active_settings.host,
        port=active_settings.port,
        reload=active_settings.debug,
        log_level=active_settings.log_level.lower() if hasattr(active_settings, 'log_level') else "info"
    )
