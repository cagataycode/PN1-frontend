"""
API Models - Data structures for API requests and responses

This module defines the data models for:
- API request/response structures
- Error handling
- Pagination and filtering
- Status responses
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Generic, TypeVar

T = TypeVar('T')
from datetime import datetime
from enum import Enum


class APIStatus(str, Enum):
    """API response status"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class HTTPStatusCodes:
    """Common HTTP status codes"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class APIResponse(BaseModel, Generic[TypeVar('T')]):
    """Generic API response wrapper"""
    status: APIStatus = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    timestamp: datetime = Field(..., description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {"result": "example data"},
                "timestamp": "2024-01-01T12:00:00Z",
                "request_id": "req_123",
                "metadata": {"version": "1.0"}
            }
        }


class ErrorResponse(BaseModel):
    """Error response structure"""
    status: APIStatus = Field(APIStatus.ERROR, description="Response status")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Application error code")
    error_type: Optional[str] = Field(None, description="Type of error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    path: Optional[str] = Field(None, description="Request path")
    method: Optional[str] = Field(None, description="HTTP method")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "error_type": "ValidationError",
                "details": {"field": "name", "issue": "Field is required"},
                "timestamp": "2024-01-01T12:00:00Z",
                "request_id": "req_123",
                "path": "/api/assess",
                "method": "POST"
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    page: int = Field(1, description="Page number", ge=1)
    size: int = Field(20, description="Page size", ge=1, le=100)
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort order (asc/desc)")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v.lower() if v else 'asc'


class PaginatedResponse(BaseModel, Generic[TypeVar('T')]):
    """Paginated response wrapper"""
    items: List[T] = Field(..., description="List of items")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "Example"}],
                "pagination": {
                    "page": 1,
                    "size": 20,
                    "total": 100,
                    "pages": 5
                },
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (development/production)")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Individual service health")
    database: Optional[Dict[str, Any]] = Field(None, description="Database health status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "1.0.0",
                "environment": "development",
                "uptime": 3600.5,
                "services": {
                    "dpq": {"status": "active"},
                    "claude": {"status": "active"},
                    "video": {"status": "active"}
                },
                "database": {"status": "connected"}
            }
        }


class FileUploadResponse(BaseModel):
    """File upload response"""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File MIME type")
    upload_url: Optional[str] = Field(None, description="URL where file was uploaded")
    processing_status: str = Field(..., description="Current processing status")
    created_at: datetime = Field(..., description="Upload timestamp")
    expires_at: Optional[datetime] = Field(None, description="When file expires")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional file metadata")


class SearchParams(BaseModel):
    """Search parameters for search endpoints"""
    query: str = Field(..., description="Search query", min_length=1)
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    include_archived: bool = Field(False, description="Include archived items")
    date_from: Optional[datetime] = Field(None, description="Search from date")
    date_to: Optional[datetime] = Field(None, description="Search to date")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Golden Retriever",
                "filters": {"breed": "Golden Retriever", "age": "young"},
                "include_archived": False,
                "date_from": "2024-01-01T00:00:00Z",
                "date_to": "2024-12-31T23:59:59Z"
            }
        }


class BulkOperationResponse(BaseModel):
    """Response for bulk operations"""
    operation: str = Field(..., description="Type of operation performed")
    total_items: int = Field(..., description="Total number of items processed")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Details of failed operations")
    timestamp: datetime = Field(..., description="Operation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "operation": "bulk_delete",
                "total_items": 100,
                "successful": 95,
                "failed": 5,
                "errors": [
                    {"item_id": "123", "reason": "Item not found"}
                ],
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class WebhookPayload(BaseModel):
    """Webhook payload structure"""
    event_type: str = Field(..., description="Type of event")
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    source: str = Field(..., description="Event source")
    version: str = Field(..., description="Webhook version")
    
    class Config:
        schema_extra = {
            "example": {
                "event_type": "assessment.completed",
                "event_id": "evt_123",
                "timestamp": "2024-01-01T12:00:00Z",
                "data": {"assessment_id": "assess_456"},
                "source": "dpq-backend",
                "version": "1.0"
            }
        }
