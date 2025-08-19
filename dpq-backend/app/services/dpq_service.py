"""
DPQ Service - Handles Dog Personality Questionnaire analysis and scoring

This service encapsulates the business logic for:
- Processing DPQ responses
- Calculating factor and facet scores
- Generating personality profiles
- Managing assessment results
"""

import sys
import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json

# Add the dpq directory to the path so we can import the existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'dpq'))

from dpq.dpq import DogPersonalityQuestionnaire, DPQResults
from dpq.response_formatter import DPQResponseFormatter

logger = logging.getLogger(__name__)


class DPQService:
    """
    Service class for handling DPQ analysis operations
    """
    
    def __init__(self):
        """Initialize the DPQ service"""
        self.dpq_analyzer = DogPersonalityQuestionnaire()
        self.response_formatter = DPQResponseFormatter()
        logger.info("DPQ Service initialized")
    
    async def process_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete DPQ assessment
        
        Args:
            assessment_data: Dictionary containing assessment information and responses
            
        Returns:
            Dictionary containing processed assessment results
        """
        try:
            logger.info(f"Processing assessment for dog: {assessment_data.get('dog_name', 'Unknown')}")
            
            # Extract the questionnaire responses
            responses = assessment_data.get('responses', {})
            dog_info = assessment_data.get('dog_info', {})
            
            # Validate responses
            if not self._validate_responses(responses):
                raise ValueError("Invalid response format or missing required responses")
            
            # Process the assessment using the existing DPQ logic
            results = await self._analyze_personality(responses, dog_info)
            
            # Format the response
            formatted_results = await self._format_results(results, dog_info)
            
            logger.info(f"Assessment processed successfully for dog: {dog_info.get('name', 'Unknown')}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error processing assessment: {str(e)}")
            raise
    
    async def _analyze_personality(self, responses: Dict[int, int], dog_info: Dict[str, Any]) -> DPQResults:
        """
        Analyze personality using the existing DPQ logic
        
        Args:
            responses: Dictionary mapping question numbers to response values (1-5)
            dog_info: Dictionary containing dog information
            
        Returns:
            DPQResults object containing analysis results
        """
        try:
            # Convert responses to the format expected by the DPQ analyzer
            # The existing code expects responses as a dictionary with question numbers as keys
            processed_responses = {}
            for q_num, response in responses.items():
                if isinstance(q_num, str):
                    q_num = int(q_num)
                processed_responses[q_num] = response
            
            # Use the existing DPQ analysis logic
            results = self.dpq_analyzer.analyze_responses(processed_responses)
            
            # Add dog information to results
            results.dog_id = dog_info.get('id', f"dog_{datetime.now().timestamp()}")
            results.assessment_date = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in personality analysis: {str(e)}")
            raise
    
    async def _format_results(self, results: DPQResults, dog_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the results for API response
        
        Args:
            results: DPQResults object from analysis
            dog_info: Dictionary containing dog information
            
        Returns:
            Formatted results dictionary
        """
        try:
            # Use the existing response formatter
            formatted = self.response_formatter.format_assessment_response(
                dpq_results=results,
                dog_info=dog_info,
                user_id="test_user",
                assessment_metadata={
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "assessment_duration_minutes": 5,
                    "device_type": "web",
                    "app_version": "1.0"
                },
                responses={str(k): v for k, v in results.raw_scores.items()}
            )
            
            # Add additional metadata
            formatted.update({
                "dog_info": dog_info,
                "assessment_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_questions": len(results.raw_scores)
                }
            })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting results: {str(e)}")
            raise
    
    def _validate_responses(self, responses: Dict[int, int]) -> bool:
        """
        Validate that responses are in the correct format
        
        Args:
            responses: Dictionary of question responses
            
        Returns:
            True if valid, False otherwise
        """
        if not responses:
            return False
        
        # Check that all responses are valid (1-5 scale)
        valid_values = {1, 2, 3, 4, 5}
        for question_num, response in responses.items():
            if not isinstance(question_num, (int, str)) or not isinstance(response, int):
                return False
            if response not in valid_values:
                return False
        
        return True
    
    async def get_assessment_summary(self, assessment_id: str) -> Dict[str, Any]:
        """
        Get a summary of a specific assessment
        
        Args:
            assessment_id: Unique identifier for the assessment
            
        Returns:
            Assessment summary dictionary
        """
        try:
            # This would typically query a database
            # For now, return a placeholder
            logger.info(f"Retrieving assessment summary for ID: {assessment_id}")
            
            return {
                "assessment_id": assessment_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving assessment summary: {str(e)}")
            raise
    
    async def get_personality_factors(self) -> Dict[str, List[str]]:
        """
        Get information about the personality factors measured by DPQ
        
        Returns:
            Dictionary describing personality factors and their facets
        """
        try:
            # Return the factor structure from the DPQ analyzer
            return {
                "factors": {
                    "Neuroticism": ["Fear", "Anxiety", "Aggression"],
                    "Extraversion": ["Sociability", "Activity", "Playfulness"],
                    "Openness": ["Curiosity", "Problem-solving", "Trainability"],
                    "Agreeableness": ["Affection", "Cooperation", "Trust"],
                    "Conscientiousness": "Trainability"
                },
                "description": "The DPQ measures 5 major personality factors in dogs, each with specific behavioral facets."
            }
            
        except Exception as e:
            logger.error(f"Error retrieving personality factors: {str(e)}")
            raise
