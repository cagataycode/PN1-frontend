"""
Service Manager - Coordinates all services and provides unified interface

This service manager handles:
- Service initialization and lifecycle management
- Coordinated operations across multiple services
- Error handling and fallback strategies
- Service health monitoring
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dpq_service import DPQService
from .claude_service import ClaudeService
from .video_service import VideoService

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Manages all services and provides coordinated operations
    """
    
    def __init__(self):
        """Initialize the service manager and all services"""
        self.services = {}
        self.service_status = {}
        self.initialized = False
        
        try:
            self._initialize_services()
            self.initialized = True
            logger.info("Service Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Service Manager: {str(e)}")
            raise
    
    def _initialize_services(self):
        """Initialize all individual services"""
        try:
            # Initialize DPQ Service
            self.services['dpq'] = DPQService()
            logger.info("DPQ Service initialized")
            
            # Initialize Claude Service
            self.services['claude'] = ClaudeService()
            logger.info("Claude Service initialized")
            
            # Initialize Video Service
            self.services['video'] = VideoService()
            logger.info("Video Service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise
    
    async def process_complete_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete assessment including personality analysis and recommendations
        
        Args:
            assessment_data: Dictionary containing assessment information and responses
            
        Returns:
            Complete assessment results with recommendations
        """
        try:
            if not self.initialized:
                raise RuntimeError("Service Manager not properly initialized")
            
            logger.info(f"Processing complete assessment for dog: {assessment_data.get('dog_info', {}).get('name', 'Unknown')}")
            
            # Step 1: Process DPQ assessment
            dpq_results = await self.services['dpq'].process_assessment(assessment_data)
            
            # Step 2: Generate AI recommendations
            recommendations = await self.services['claude'].generate_recommendations(dpq_results)
            
            # Step 3: Combine results
            complete_results = {
                "assessment_id": f"assessment_{datetime.now().timestamp()}",
                "status": "completed",
                "dpq_results": dpq_results,
                "ai_recommendations": recommendations,
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "services_used": ["dpq", "claude"],
                    "dog_name": assessment_data.get('dog_info', {}).get('name', 'Unknown')
                }
            }
            
            logger.info(f"Complete assessment processed successfully for dog: {assessment_data.get('dog_info', {}).get('name', 'Unknown')}")
            return complete_results
            
        except Exception as e:
            logger.error(f"Error processing complete assessment: {str(e)}")
            raise
    
    async def process_video_assessment(self, video_file_path: str, dog_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process video assessment and integrate with personality analysis
        
        Args:
            video_file_path: Path to the uploaded video file
            dog_info: Dictionary containing dog information
            
        Returns:
            Video analysis results with behavioral insights
        """
        try:
            if not self.initialized:
                raise RuntimeError("Service Manager not properly initialized")
            
            logger.info(f"Processing video assessment for dog: {dog_info.get('name', 'Unknown')}")
            
            # Process video using video service
            video_results = await self.services['video'].process_video(video_file_path, dog_info)
            
            # Generate behavioral insights using Claude service
            behavior_insights = await self.services['claude'].analyze_behavior_insights(video_results)
            
            # Combine results
            complete_video_results = {
                "video_analysis": video_results,
                "behavior_insights": behavior_insights,
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "services_used": ["video", "claude"],
                    "dog_name": dog_info.get('name', 'Unknown')
                }
            }
            
            logger.info(f"Video assessment processed successfully for dog: {dog_info.get('name', 'Unknown')}")
            return complete_video_results
            
        except Exception as e:
            logger.error(f"Error processing video assessment: {str(e)}")
            raise
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get health status of all services
        
        Returns:
            Dictionary with health status of all services
        """
        try:
            health_status = {
                "overall_status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {}
            }
            
            # Check each service
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, 'get_service_status'):
                        status = await service.get_service_status()
                        health_status["services"][service_name] = status
                        
                        # Check if service is healthy
                        if status.get('status') != 'active':
                            health_status["overall_status"] = "degraded"
                    else:
                        health_status["services"][service_name] = {
                            "status": "unknown",
                            "note": "Service status method not available"
                        }
                        
                except Exception as e:
                    health_status["services"][service_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    health_status["overall_status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting service health: {str(e)}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """
        Get capabilities and features of all services
        
        Returns:
            Dictionary describing service capabilities
        """
        try:
            capabilities = {
                "dpq_service": {
                    "description": "Dog Personality Questionnaire analysis and scoring",
                    "features": [
                        "Process DPQ responses",
                        "Calculate factor and facet scores",
                        "Generate personality profiles",
                        "Validate assessment data"
                    ]
                },
                "claude_service": {
                    "description": "AI-powered recommendations using Claude API",
                    "features": [
                        "Personalized training recommendations",
                        "Care and exercise suggestions",
                        "Behavior insights analysis",
                        "Fallback recommendation system"
                    ]
                },
                "video_service": {
                    "description": "Video processing and behavioral analysis",
                    "features": [
                        "Video upload and validation",
                        "Frame extraction using FFmpeg",
                        "Behavior analysis with Claude API",
                        "Temporary file management"
                    ]
                }
            }
            
            return capabilities
            
        except Exception as e:
            logger.error(f"Error getting service capabilities: {str(e)}")
            raise
    
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """
        Restart a specific service
        
        Args:
            service_name: Name of the service to restart
            
        Returns:
            Status of the restart operation
        """
        try:
            if service_name not in self.services:
                raise ValueError(f"Unknown service: {service_name}")
            
            logger.info(f"Restarting service: {service_name}")
            
            # Reinitialize the specific service
            if service_name == 'dpq':
                self.services[service_name] = DPQService()
            elif service_name == 'claude':
                self.services[service_name] = ClaudeService()
            elif service_name == 'video':
                self.services[service_name] = VideoService()
            
            logger.info(f"Service {service_name} restarted successfully")
            
            return {
                "service": service_name,
                "status": "restarted",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {str(e)}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown all services"""
        try:
            logger.info("Shutting down Service Manager...")
            
            # Clean up services
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, '__del__'):
                        service.__del__()
                    logger.info(f"Service {service_name} shut down")
                except Exception as e:
                    logger.warning(f"Error shutting down service {service_name}: {str(e)}")
            
            self.services.clear()
            self.initialized = False
            
            logger.info("Service Manager shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def is_healthy(self) -> bool:
        """
        Check if the service manager is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        return self.initialized and len(self.services) > 0
    
    def get_service(self, service_name: str):
        """
        Get a specific service by name
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance or None if not found
        """
        return self.services.get(service_name)
    
    def list_services(self) -> List[str]:
        """
        Get list of available service names
        
        Returns:
            List of service names
        """
        return list(self.services.keys())
