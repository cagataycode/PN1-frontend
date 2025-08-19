"""
API Routes Package

This package contains all the API route modules for the DPQ backend.
"""

from .assessments import router as assessments_router
from .videos import router as videos_router

# Export all routers
__all__ = [
    "assessments_router",
    "videos_router"
]
