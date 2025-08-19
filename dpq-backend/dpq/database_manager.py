# api_handler.py - Main API logic to coordinate DPQ assessment flow

import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import your existing DPQ classes
from .dpq import DogPersonalityQuestionnaire, DPQAnalyzer
from .response_formatter import DPQResponseFormatter

class DPQAPIHandler:
    """
    Main API handler that coordinates the complete DPQ assessment flow:
    1. Process frontend JSON input
    2. Run DPQ analysis
    3. Format results for frontend
    4. Handle database operations
    """
    
    def __init__(self):
        self.dpq = DogPersonalityQuestionnaire()
        self.analyzer = DPQAnalyzer()
        self.formatter = DPQResponseFormatter()
    
    def process_assessment(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to process a complete DPQ assessment request
        
        Args:
            request_data: JSON from frontend matching input format
            
        Returns:
            Formatted JSON response for frontend
        """
        try:
            # 1. Extract and validate input data
            dog_info = request_data.get('dog_info', {})
            user_id = request_data.get('user_id')
            responses = request_data.get('responses', {})
            metadata = request_data.get('assessment_metadata', {})
            
            # Validate required fields
            if not user_id:
                raise ValueError("user_id is required")
            if not responses or len(responses) != 45:
                raise ValueError("45 responses are required")
            if not dog_info.get('name'):
                raise ValueError("Dog name is required")
            
            # 2. Convert string keys to integers for DPQ processing
            numeric_responses = {int(k): v for k, v in responses.items()}
            
            # 3. Run DPQ analysis
            dpq_results = self._run_dpq_analysis(numeric_responses)
            
            # 4. Format response for frontend
            formatted_response = self.formatter.format_assessment_response(
                dpq_results=dpq_results,
                dog_info=dog_info,
                user_id=user_id,
                assessment_metadata=metadata,
                responses=responses
            )
            
            # 5. Add success status
            formatted_response['status'] = 'success'
            formatted_response['message'] = 'Assessment completed successfully'
            
            return formatted_response
            
        except Exception as e:
            # Return error response
            return {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__
            }
    
    def _run_dpq_analysis(self, responses: Dict[int, int]) -> Dict[str, Any]:
        """
        Run the core DPQ analysis using your existing classes
        
        Args:
            responses: Dict with integer keys (1-45) and integer values (1-7)
            
        Returns:
            DPQ analysis results
        """
        # Validate responses are in correct range
        for question_num, response in responses.items():
            if not (1 <= question_num <= 45):
                raise ValueError(f"Invalid question number: {question_num}")
            if not (1 <= response <= 7):
                raise ValueError(f"Invalid response value: {response} for question {question_num}")
        
        # Score the assessment using your existing DPQ classes
        factor_scores = self.dpq.score_assessment(responses)
        bias_indicators = self.analyzer.calculate_bias_indicators(responses, factor_scores)
        personality_profile = self.analyzer.generate_personality_profile(factor_scores, bias_indicators)
        
        return {
            'factor_scores': factor_scores,
            'bias_indicators': bias_indicators,
            'personality_profile': personality_profile
        }
    
    def validate_input_format(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that input matches expected format
        
        Args:
            request_data: JSON from frontend
            
        Returns:
            Validation result with errors if any
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ['dog_info', 'user_id', 'responses']
        for field in required_fields:
            if field not in request_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate dog_info
        dog_info = request_data.get('dog_info', {})
        if not dog_info.get('name'):
            errors.append("Dog name is required")
        
        # Validate responses
        responses = request_data.get('responses', {})
        if len(responses) != 45:
            errors.append(f"Expected 45 responses, got {len(responses)}")
        
        # Check response values are in valid range
        for question, response in responses.items():
            try:
                q_num = int(question)
                r_val = int(response)
                if not (1 <= q_num <= 45):
                    errors.append(f"Invalid question number: {q_num}")
                if not (1 <= r_val <= 7):
                    errors.append(f"Invalid response value: {r_val} for question {q_num}")
            except (ValueError, TypeError):
                errors.append(f"Invalid question/response format: {question}={response}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }