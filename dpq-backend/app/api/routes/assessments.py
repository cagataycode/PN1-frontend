"""
Assessment API Routes

This module provides the core API endpoints for:
- Assessment submission
- Assessment retrieval
- Assessment management
- Video upload and analysis
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
import uuid
from datetime import datetime

from app.models.api_models import (
    APIResponse, ErrorResponse, APIStatus, HTTPStatusCodes,
    PaginationParams, PaginatedResponse
)
from app.models.assessment_models import (
    AssessmentRequest, AssessmentData, AssessmentStatus,
    AssessmentResponse, PersonalityProfile
)
from app.services.service_manager import ServiceManager
from app.services.dpq_service import DPQService
from app.services.claude_service import ClaudeService
from app.services.video_service import VideoService

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/assessments", tags=["assessments"])

# Service manager instance
service_manager = ServiceManager()


@router.post("/assess", response_model=APIResponse[AssessmentData])
async def create_assessment(
    assessment_request: AssessmentRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new DPQ assessment
    
    This endpoint accepts assessment data and processes it in the background.
    Returns the assessment ID immediately for tracking progress.
    """
    try:
        logger.info(f"Creating new assessment for dog: {assessment_request.dog_info.name}")
        
        # Generate unique assessment ID
        assessment_id = str(uuid.uuid4())
        
        # Create assessment data
        assessment_data = AssessmentData(
            assessment_id=assessment_id,
            dog_info=assessment_request.dog_info,
            responses=assessment_request.responses,
            status=AssessmentStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={
                "include_recommendations": assessment_request.include_recommendations,
                "include_video_analysis": assessment_request.include_video_analysis,
                "total_questions": len(assessment_request.responses)
            }
        )
        
        # Add background task for processing
        background_tasks.add_task(
            process_assessment,
            assessment_data,
            assessment_request.include_recommendations,
            assessment_request.include_video_analysis
        )
        
        logger.info(f"Assessment {assessment_id} created successfully")
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Assessment created successfully",
            data=assessment_data,
            timestamp=datetime.utcnow(),
            request_id=assessment_id,
            metadata={"processing_status": "queued"}
        )
        
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )


@router.get("/{assessment_id}", response_model=APIResponse[AssessmentData])
async def get_assessment(assessment_id: str):
    """
    Retrieve assessment data by ID
    
    Returns the current assessment data including status and results if available.
    """
    try:
        logger.info(f"Retrieving assessment: {assessment_id}")
        
        # Get assessment from service manager
        assessment = service_manager.get_assessment(assessment_id)
        
        if not assessment:
            raise HTTPException(
                status_code=HTTPStatusCodes.NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Assessment retrieved successfully",
            data=assessment,
            timestamp=datetime.utcnow(),
            request_id=assessment_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment {assessment_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment: {str(e)}"
        )


@router.get("/{assessment_id}/result", response_model=APIResponse[AssessmentResponse])
async def get_assessment_result(assessment_id: str):
    """
    Retrieve assessment results by ID
    
    Returns the complete assessment results including personality scores and recommendations.
    """
    try:
        logger.info(f"Retrieving results for assessment: {assessment_id}")
        
        # Get assessment result from service manager
        result = service_manager.get_assessment_result(assessment_id)
        
        if not result:
            raise HTTPException(
                status_code=HTTPStatusCodes.NOT_FOUND,
                detail=f"Assessment result {assessment_id} not found"
            )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Assessment result retrieved successfully",
            data=result,
            timestamp=datetime.utcnow(),
            request_id=assessment_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving result for assessment {assessment_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment result: {str(e)}"
        )


@router.post("/upload-video", response_model=APIResponse[Dict[str, Any]])
async def upload_video(
    assessment_id: Optional[str] = Form(None),
    video_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload video for assessment analysis
    
    Accepts video file upload and processes it for behavioral analysis.
    Returns upload confirmation and processing status.
    """
    try:
        logger.info(f"Uploading video for assessment: {assessment_id}")
        
        # Validate assessment exists
        assessment = service_manager.get_assessment(assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=HTTPStatusCodes.NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )
        
        # Validate file type
        if not video_file.content_type or not video_file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=HTTPStatusCodes.BAD_REQUEST,
                detail="File must be a video"
            )
        
        # Process video upload in background
        background_tasks.add_task(
            process_video_upload,
            assessment_id,
            video_file
        )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Video uploaded successfully",
            data={
                "assessment_id": assessment_id,
                "filename": video_file.filename,
                "content_type": video_file.content_type,
                "size": video_file.size,
                "processing_status": "queued"
            },
            timestamp=datetime.utcnow(),
            request_id=assessment_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video for assessment {assessment_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )








# Background task functions
async def process_assessment(
    assessment_data: AssessmentData,
    include_recommendations: bool,
    include_video_analysis: bool
):
    """Background task to process assessment"""
    try:
        logger.info(f"Processing assessment {assessment_data.assessment_id}")
        
        # Update status to in progress
        service_manager.update_assessment_status(
            assessment_data.assessment_id,
            AssessmentStatus.IN_PROGRESS
        )
        
        # Process DPQ responses
        dpq_service = DPQService()
        factor_scores, facet_scores = dpq_service.analyze_responses(
            assessment_data.responses
        )
        
        # Get AI recommendations if requested
        recommendations = None
        if include_recommendations:
            claude_service = ClaudeService()
            recommendations = claude_service.generate_recommendations(
                assessment_data.dog_info,
                factor_scores,
                facet_scores
            )
        
        # Create assessment result
        result = AssessmentResponse(
            assessment_id=assessment_data.assessment_id,
            status=AssessmentStatus.COMPLETED,
            dog_info=assessment_data.dog_info,
            dpq_results=dpq_service.create_dpq_results(assessment_data.responses),
            ai_recommendations=recommendations,
            video_analysis=None,
            metadata={
                "include_recommendations": include_recommendations,
                "include_video_analysis": include_video_analysis
            },
            created_at=datetime.utcnow(),
            processed_at=datetime.utcnow()
        )
        
        # Save result
        service_manager.save_assessment_result(result)
        
        # Update assessment status
        service_manager.update_assessment_status(
            assessment_data.assessment_id,
            AssessmentStatus.COMPLETED
        )
        
        logger.info(f"Assessment {assessment_data.assessment_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing assessment {assessment_data.assessment_id}: {str(e)}", exc_info=True)
        service_manager.update_assessment_status(
            assessment_data.assessment_id,
            AssessmentStatus.FAILED
        )


async def process_video_upload(assessment_id: str, video_file: UploadFile):
    """Background task to process video upload"""
    try:
        logger.info(f"Processing video upload for assessment {assessment_id}")
        
        # Process video using video service
        video_service = VideoService()
        analysis_result = await video_service.analyze_video(
            video_file,
            assessment_id
        )
        
        # Update assessment with video analysis results
        service_manager.update_assessment_video_analysis(
            assessment_id,
            analysis_result
        )
        
        logger.info(f"Video analysis completed for assessment {assessment_id}")
        
    except Exception as e:
        logger.error(f"Error processing video for assessment {assessment_id}: {str(e)}", exc_info=True)
        # Update assessment with video analysis failure
        service_manager.update_assessment_video_analysis(
            assessment_id,
            {"error": str(e), "status": "failed"}
        )
