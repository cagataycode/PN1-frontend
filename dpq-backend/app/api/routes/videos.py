"""
Video Processing API Routes

This module provides API endpoints for:
- Video upload and processing
- Video analysis results
- Video management and cleanup
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
import uuid
from datetime import datetime

from app.models.api_models import (
    APIResponse, ErrorResponse, APIStatus, HTTPStatusCodes
)
from app.services.video_service import VideoService
from app.services.service_manager import ServiceManager

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/videos", tags=["videos"])

# Service instances
video_service = VideoService()
service_manager = ServiceManager()


@router.post("/process", response_model=APIResponse[Dict[str, Any]])
async def process_video(
    video_file: UploadFile = File(...),
    assessment_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload and process a video file
    
    Accepts video file upload and processes it for behavioral analysis.
    Can be associated with an assessment or processed independently.
    """
    try:
        logger.info(f"Processing video upload: {video_file.filename}")
        
        # Validate file type
        if not video_file.content_type or not video_file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=HTTPStatusCodes.BAD_REQUEST,
                detail="File must be a video"
            )
        
        # Validate file size (check if we need to add this to config)
        max_size = 100 * 1024 * 1024  # 100MB default
        if video_file.size and video_file.size > max_size:
            raise HTTPException(
                status_code=HTTPStatusCodes.BAD_REQUEST,
                detail=f"Video file too large. Maximum size: {max_size / (1024*1024):.1f}MB"
            )
        
        # Generate video ID
        video_id = str(uuid.uuid4())
        
        # Process video in background
        background_tasks.add_task(
            process_video_analysis,
            video_id,
            video_file,
            assessment_id,
            description
        )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Video uploaded successfully",
            data={
                "video_id": video_id,
                "filename": video_file.filename,
                "content_type": video_file.content_type,
                "size": video_file.size,
                "assessment_id": assessment_id,
                "description": description,
                "processing_status": "queued"
            },
            timestamp=datetime.utcnow(),
            request_id=video_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )








@router.post("/{video_id}/reprocess", response_model=APIResponse[Dict[str, Any]])
async def reprocess_video(
    video_id: str,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Reprocess a video for analysis
    
    Triggers a new analysis of an existing video.
    """
    try:
        logger.info(f"Reprocessing video: {video_id}")
        
        # Check if video exists
        video_info = video_service.get_video_info(video_id)
        if not video_info:
            raise HTTPException(
                status_code=HTTPStatusCodes.NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        # Add reprocessing task
        background_tasks.add_task(
            reprocess_video_analysis,
            video_id
        )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Video reprocessing started",
            data={
                "video_id": video_id,
                "status": "reprocessing",
                "timestamp": datetime.utcnow().isoformat()
            },
            timestamp=datetime.utcnow(),
            request_id=video_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting video reprocessing {video_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to start video reprocessing: {str(e)}"
        )


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """
    Delete video and all associated data
    
    Removes the video file and analysis results.
    """
    try:
        logger.info(f"Deleting video: {video_id}")
        
        # Delete video using service
        success = video_service.delete_video(video_id)
        
        if not success:
            raise HTTPException(
                status_code=HTTPStatusCodes.NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Video deleted successfully",
            data={"video_id": video_id},
            timestamp=datetime.utcnow(),
            request_id=video_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete video: {str(e)}"
        )


@router.get("/", response_model=APIResponse[List[Dict[str, Any]]])
async def list_videos(
    assessment_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List videos with optional filtering
    
    Returns list of videos with optional filtering by assessment and status.
    """
    try:
        logger.info(f"Listing videos with filters: assessment_id={assessment_id}, status={status}")
        
        # Get videos from service
        videos = video_service.list_videos(
            assessment_id=assessment_id,
            status=status,
            limit=limit
        )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Videos retrieved successfully",
            data=videos,
            timestamp=datetime.utcnow(),
            metadata={
                "total_count": len(videos),
                "filters": {
                    "assessment_id": assessment_id,
                    "status": status,
                    "limit": limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to list videos: {str(e)}"
        )


# Background task functions
async def process_video_analysis(
    video_id: str,
    video_file: UploadFile,
    assessment_id: Optional[str],
    description: Optional[str]
):
    """Background task to process video analysis"""
    try:
        logger.info(f"Processing video analysis for {video_id}")
        
        # Process video using video service
        analysis_result = await video_service.analyze_video(
            video_file,
            video_id,
            assessment_id=assessment_id,
            description=description
        )
        
        logger.info(f"Video analysis completed for {video_id}")
        
    except Exception as e:
        logger.error(f"Error processing video analysis for {video_id}: {str(e)}", exc_info=True)
        # Update video status to failed
        video_service.update_video_status(video_id, "failed", {"error": str(e)})


async def reprocess_video_analysis(video_id: str):
    """Background task to reprocess video analysis"""
    try:
        logger.info(f"Reprocessing video analysis for {video_id}")
        
        # Reprocess video using video service
        analysis_result = await video_service.reprocess_video(video_id)
        
        logger.info(f"Video reprocessing completed for {video_id}")
        
    except Exception as e:
        logger.error(f"Error reprocessing video {video_id}: {str(e)}", exc_info=True)
        # Update video status to failed
        video_service.update_video_status(video_id, "failed", {"error": str(e)})
