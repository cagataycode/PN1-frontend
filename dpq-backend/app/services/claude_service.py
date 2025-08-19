"""
Claude Service - Handles AI-powered recommendations using Claude API

This service encapsulates the business logic for:
- Generating personalized training recommendations
- Analyzing dog behavior insights
- Providing care and exercise suggestions
- Managing Claude API interactions
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime

# Add the dpq directory to the path so we can import the existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'dpq'))

from dpq.claude_recommender import ClaudeRecommendationGenerator, DogPersonalityProfile

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Service class for handling Claude API operations and recommendations
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Claude service
        
        Args:
            api_key: Anthropic API key. If None, will try to get from environment
        """
        try:
            self.claude_generator = ClaudeRecommendationGenerator(api_key=api_key)
            logger.info("Claude Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude Service: {str(e)}")
            raise
    
    async def generate_recommendations(self, personality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations using Claude API
        
        Args:
            personality_data: Dictionary containing DPQ results and dog information
            
        Returns:
            Dictionary with categorized recommendations
        """
        try:
            logger.info(f"Generating recommendations for dog: {personality_data.get('dog_info', {}).get('name', 'Unknown')}")
            
            # Validate input data
            if not self._validate_personality_data(personality_data):
                raise ValueError("Invalid personality data format")
            
            # Prepare data for Claude
            claude_data = self._prepare_claude_data(personality_data)
            
            # Generate recommendations using the existing Claude logic
            recommendations = await self._call_claude_api(claude_data)
            
            # Add metadata to recommendations
            recommendations.update({
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model": "claude-sonnet-4-20250514",
                    "dog_name": personality_data.get('dog_info', {}).get('name', 'Unknown')
                }
            })
            
            logger.info(f"Recommendations generated successfully for dog: {personality_data.get('dog_info', {}).get('name', 'Unknown')}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            # Return fallback recommendations
            return await self._get_fallback_recommendations(personality_data)
    
    async def _call_claude_api(self, personality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Claude API to generate recommendations
        
        Args:
            personality_data: Formatted data for Claude API
            
        Returns:
            Claude API response with recommendations
        """
        try:
            # Use the existing Claude generator
            recommendations = self.claude_generator.generate_recommendations(personality_data)
            
            # Ensure the response is properly formatted
            if not isinstance(recommendations, dict):
                logger.warning("Claude API returned unexpected response format")
                return await self._get_fallback_recommendations(personality_data)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return await self._get_fallback_recommendations(personality_data)
    
    def _prepare_claude_data(self, personality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare personality data for Claude API consumption
        
        Args:
            personality_data: Raw personality data from DPQ
            
        Returns:
            Formatted data ready for Claude API
        """
        try:
            # Extract key components
            dog_info = personality_data.get('dog_info', {})
            factor_scores = personality_data.get('factor_scores', {})
            facet_scores = personality_data.get('facet_scores', {})
            personality_profile = personality_data.get('personality_profile', {})
            bias_indicators = personality_data.get('bias_indicators', {})
            
            # Format for Claude API
            claude_data = {
                "dog_info": dog_info,
                "factor_scores": factor_scores,
                "facet_scores": facet_scores,
                "personality_profile": personality_profile,
                "bias_indicators": bias_indicators
            }
            
            return claude_data
            
        except Exception as e:
            logger.error(f"Error preparing Claude data: {str(e)}")
            raise
    
    def _validate_personality_data(self, personality_data: Dict[str, Any]) -> bool:
        """
        Validate that personality data contains required fields
        
        Args:
            personality_data: Dictionary containing personality assessment data
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['dog_info', 'factor_scores']
        
        for field in required_fields:
            if field not in personality_data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check that dog_info has at least a name
        dog_info = personality_data.get('dog_info', {})
        if not dog_info.get('name'):
            logger.warning("Dog info missing name")
            return False
        
        # Check that factor_scores is not empty
        factor_scores = personality_data.get('factor_scores', {})
        if not factor_scores:
            logger.warning("Factor scores are empty")
            return False
        
        return True
    
    async def _get_fallback_recommendations(self, personality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide fallback recommendations when Claude API fails
        
        Args:
            personality_data: Original personality data
            
        Returns:
            Basic fallback recommendations
        """
        try:
            dog_name = personality_data.get('dog_info', {}).get('name', 'your dog')
            
            fallback_recommendations = {
                "training_tips": [
                    "Start with basic obedience training using positive reinforcement",
                    "Keep training sessions short (5-10 minutes) and fun",
                    "Use treats and praise to reward good behavior",
                    "Be consistent with commands and expectations"
                ],
                "exercise_needs": [
                    "Provide daily physical exercise appropriate for your dog's age and breed",
                    "Include mental stimulation through puzzle toys and training",
                    "Allow for regular playtime and social interaction",
                    "Monitor your dog's energy levels and adjust accordingly"
                ],
                "socialization": [
                    "Gradually expose your dog to new people, places, and situations",
                    "Use positive experiences to build confidence",
                    "Consider puppy socialization classes if appropriate",
                    "Monitor your dog's comfort level and don't force interactions"
                ],
                "daily_care": [
                    "Establish a consistent daily routine",
                    "Provide a safe, comfortable environment",
                    "Ensure regular veterinary check-ups",
                    "Maintain proper nutrition and hydration"
                ],
                "ai_communication": [
                    "Pay attention to your dog's body language and vocalizations",
                    "Learn to recognize signs of stress, fear, or discomfort",
                    "Use clear, consistent signals when communicating",
                    "Build trust through positive interactions and respect for boundaries"
                ],
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model": "fallback",
                    "note": "These are general recommendations. For personalized advice, please try again later.",
                    "dog_name": dog_name
                }
            }
            
            logger.info(f"Fallback recommendations generated for dog: {dog_name}")
            return fallback_recommendations
            
        except Exception as e:
            logger.error(f"Error generating fallback recommendations: {str(e)}")
            # Return minimal fallback
            return {
                "training_tips": ["Start with basic obedience training using positive reinforcement"],
                "exercise_needs": ["Provide daily physical exercise appropriate for your dog's age and breed"],
                "socialization": ["Gradually expose your dog to new people, places, and situations"],
                "daily_care": ["Establish a consistent daily routine"],
                "ai_communication": ["Pay attention to your dog's body language and vocalizations"],
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model": "fallback",
                    "note": "Basic recommendations due to system error"
                }
            }
    
    async def analyze_behavior_insights(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze behavior insights using Claude API
        
        Args:
            behavior_data: Dictionary containing behavior observations
            
        Returns:
            Dictionary with behavior analysis and insights
        """
        try:
            logger.info("Analyzing behavior insights with Claude API")
            
            # This would integrate with the behavior analysis from video processing
            # For now, return a placeholder
            return {
                "insights": "Behavior analysis feature coming soon",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing behavior insights: {str(e)}")
            raise
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Claude service
        
        Returns:
            Dictionary with service status information
        """
        try:
            return {
                "service": "Claude Service",
                "status": "active",
                "api_available": True,
                "last_check": datetime.now().isoformat(),
                "features": [
                    "Personalized training recommendations",
                    "Care and exercise suggestions",
                    "Behavior insights analysis",
                    "Fallback recommendation system"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")
            return {
                "service": "Claude Service",
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
