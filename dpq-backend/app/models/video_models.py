"""
Video Models - Data structures for video processing and analysis

This module defines the data models for:
- Video upload requests
- Video processing status
- Video analysis results
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    """Status of video processing"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoFormat(str, Enum):
    """Supported video formats"""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    MKV = "mkv"
    WMV = "wmv"
    FLV = "flv"


class VideoUploadRequest(BaseModel):
    """Request model for video upload"""
    assessment_id: Optional[str] = Field(None, description="Associated assessment ID", max_length=100)
    description: Optional[str] = Field(None, description="Video description", max_length=500)
    tags: Optional[List[str]] = Field(None, description="Video tags for categorization", max_items=10)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            for tag in v:
                if not tag.strip() or len(tag.strip()) > 50:
                    raise ValueError('Tags must be non-empty and under 50 characters')
        return v


class VideoFileInfo(BaseModel):
    """Video file information and metadata"""
    filename: str = Field(..., description="Original filename", min_length=1, max_length=255)
    content_type: str = Field(..., description="MIME type of the video")
    file_size: int = Field(..., description="File size in bytes", gt=0)
    duration: Optional[float] = Field(None, description="Video duration in seconds", gt=0)
    resolution: Optional[str] = Field(None, description="Video resolution (e.g., '1920x1080')")
    frame_rate: Optional[float] = Field(None, description="Frame rate in fps", gt=0)
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if not v.startswith('video/'):
            raise ValueError('File must be a video')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 500 * 1024 * 1024  # 500MB
        if v > max_size:
            raise ValueError(f'File size must be under {max_size / (1024*1024):.0f}MB')
        return v
    
    @validator('duration')
    def validate_duration(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Duration must be positive')
            if v > 3600:  # 1 hour
                raise ValueError('Video duration must be under 1 hour')
        return v
    
    @validator('resolution')
    def validate_resolution(cls, v):
        if v is not None:
            import re
            if not re.match(r'^\d+x\d+$', v):
                raise ValueError('Resolution must be in format "widthxheight" (e.g., "1920x1080")')
        return v


class VideoProcessingStatus(BaseModel):
    """Current status of video processing"""
    status: VideoStatus = Field(..., description="Current processing status")
    progress: Optional[float] = Field(None, description="Processing progress (0-100)", ge=0, le=100)
    current_step: Optional[str] = Field(None, description="Current processing step")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    @validator('progress')
    def validate_progress(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Progress must be between 0 and 100')
        return v


class VideoAnalysisResult(BaseModel):
    """Results of video analysis"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    video_id: str = Field(..., description="Associated video ID")
    assessment_id: Optional[str] = Field(None, description="Associated assessment ID")
    
    # Behavioral analysis results
    behavior_indicators: Dict[str, float] = Field(..., description="Behavioral indicator scores")
    activity_level: Optional[str] = Field(None, description="Overall activity level assessment")
    social_behavior: Optional[str] = Field(None, description="Social behavior assessment")
    stress_indicators: Optional[List[str]] = Field(None, description="Stress indicators detected")
    
    # Technical analysis
    frame_analysis: Optional[Dict[str, Any]] = Field(None, description="Frame-by-frame analysis data")
    motion_detection: Optional[Dict[str, Any]] = Field(None, description="Motion detection results")
    
    # Metadata
    analysis_duration: float = Field(..., description="Analysis processing time in seconds", gt=0)
    confidence_score: float = Field(..., description="Analysis confidence score", ge=0, le=1)
    created_at: datetime = Field(..., description="When analysis was completed")
    
    @validator('behavior_indicators')
    def validate_behavior_indicators(cls, v):
        if not v:
            raise ValueError('Behavior indicators cannot be empty')
        for indicator, score in v.items():
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                raise ValueError(f'Behavior indicator score must be between 0 and 100: {indicator}')
        return v
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v


class VideoMetadata(BaseModel):
    """Complete video metadata"""
    video_id: str = Field(..., description="Unique video identifier")
    file_info: VideoFileInfo = Field(..., description="Video file information")
    upload_request: VideoUploadRequest = Field(..., description="Upload request details")
    processing_status: VideoProcessingStatus = Field(..., description="Current processing status")
    analysis_result: Optional[VideoAnalysisResult] = Field(None, description="Analysis results if completed")
    
    # Timestamps
    uploaded_at: datetime = Field(..., description="When video was uploaded")
    processing_started_at: Optional[datetime] = Field(None, description="When processing started")
    processing_completed_at: Optional[datetime] = Field(None, description="When processing completed")
    
    # Storage information
    storage_path: str = Field(..., description="Path where video is stored")
    thumbnail_path: Optional[str] = Field(None, description="Path to video thumbnail")
    
    class Config:
        schema_extra = {
            "example": {
                "video_id": "vid_123",
                "file_info": {
                    "filename": "dog_behavior.mp4",
                    "content_type": "video/mp4",
                    "file_size": 10485760,
                    "duration": 120.5,
                    "resolution": "1920x1080",
                    "frame_rate": 30.0
                },
                "upload_request": {
                    "assessment_id": "assess_456",
                    "description": "Dog playing in backyard",
                    "tags": ["play", "outdoor", "social"]
                },
                "processing_status": {
                    "status": "completed",
                    "progress": 100.0,
                    "current_step": "Analysis complete"
                }
            }
        }
