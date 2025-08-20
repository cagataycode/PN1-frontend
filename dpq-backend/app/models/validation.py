"""
Validation Module - Custom validators and validation utilities

This module provides:
- Custom field validators
- Validation error messages
- Input sanitization
- Business rule validation
"""

from pydantic import validator, root_validator
from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime, timedelta


class ValidationUtils:
    """Utility class for common validation operations"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input by removing extra whitespace and special characters"""
        if not value:
            return value
        # Remove extra whitespace and normalize
        sanitized = re.sub(r'\s+', ' ', value.strip())
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        return sanitized
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_url_format(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))


class AssessmentValidators:
    """Validators specific to assessment data"""
    
    @staticmethod
    def validate_dpq_question_range(question_number: int) -> bool:
        """Validate that question number is within DPQ range"""
        return 1 <= question_number <= 50
    
    @staticmethod
    def validate_response_scale(response: int) -> bool:
        """Validate that response is within valid scale"""
        return 1 <= response <= 5
    
    @staticmethod
    def validate_assessment_completeness(responses: Dict[int, int]) -> bool:
        """Validate that assessment has sufficient responses"""
        min_questions = 30
        max_questions = 50
        
        if len(responses) < min_questions:
            return False, f"Assessment must have at least {min_questions} responses"
        
        if len(responses) > max_questions:
            return False, f"Assessment cannot have more than {max_questions} responses"
        
        return True, "Assessment completeness validated"
    
    @staticmethod
    def validate_response_consistency(responses: Dict[int, int]) -> bool:
        """Validate response consistency and detect potential bias"""
        if not responses:
            return False, "No responses provided"
        
        # Check for extreme responding bias (all 1s or all 5s)
        unique_values = set(responses.values())
        if len(unique_values) == 1:
            value = list(unique_values)[0]
            if value in [1, 5]:
                return False, f"Potential extreme responding bias detected (all responses are {value})"
        
        # Check for acquiescence bias (mostly high values)
        high_responses = sum(1 for r in responses.values() if r >= 4)
        if high_responses / len(responses) > 0.8:
            return False, "Potential acquiescence bias detected (too many high responses)"
        
        return True, "Response consistency validated"


class VideoValidators:
    """Validators specific to video data"""
    
    @staticmethod
    def validate_video_format(filename: str) -> bool:
        """Validate video file format"""
        valid_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'}
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return f'.{file_ext}' in valid_extensions
    
    @staticmethod
    def validate_video_size(file_size: int, max_size_mb: int = 500) -> bool:
        """Validate video file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def validate_video_duration(duration: float) -> bool:
        """Validate video duration"""
        min_duration = 5.0  # 5 seconds minimum
        max_duration = 3600.0  # 1 hour maximum
        return min_duration <= duration <= max_duration
    
    @staticmethod
    def validate_resolution_format(resolution: str) -> bool:
        """Validate resolution format (e.g., '1920x1080')"""
        pattern = r'^\d+x\d+$'
        if not re.match(pattern, resolution):
            return False
        
        width, height = map(int, resolution.split('x'))
        # Check reasonable bounds
        return 320 <= width <= 7680 and 240 <= height <= 4320


class BusinessRuleValidators:
    """Validators for business logic and rules"""
    
    @staticmethod
    def validate_assessment_frequency(user_id: str, last_assessment_date: datetime) -> bool:
        """Validate that user isn't submitting assessments too frequently"""
        min_interval = timedelta(hours=1)  # Minimum 1 hour between assessments
        time_since_last = datetime.utcnow() - last_assessment_date
        return time_since_last >= min_interval
    
    @staticmethod
    def validate_video_upload_limit(user_id: str, daily_uploads: int) -> bool:
        """Validate daily video upload limit"""
        max_daily_uploads = 10
        return daily_uploads < max_daily_uploads
    
    @staticmethod
    def validate_file_type_restrictions(content_type: str, allowed_types: List[str]) -> bool:
        """Validate file type restrictions"""
        return content_type in allowed_types


class CustomValidators:
    """Collection of custom validators for Pydantic models"""
    
    @staticmethod
    def validate_dog_name(name: str) -> str:
        """Validate and sanitize dog name"""
        if not name or not name.strip():
            raise ValueError('Dog name cannot be empty')
        
        sanitized = ValidationUtils.sanitize_string(name)
        if len(sanitized) < 1:
            raise ValueError('Dog name must have at least 1 character')
        if len(sanitized) > 100:
            raise ValueError('Dog name cannot exceed 100 characters')
        
        # Check for potentially inappropriate content
        inappropriate_words = ['admin', 'root', 'system', 'test', 'null', 'undefined']
        if sanitized.lower() in inappropriate_words:
            raise ValueError('Dog name contains inappropriate content')
        
        return sanitized
    
    @staticmethod
    def validate_breed_name(breed: Optional[str]) -> Optional[str]:
        """Validate and sanitize breed name"""
        if breed is None:
            return breed
        
        sanitized = ValidationUtils.sanitize_string(breed)
        if len(sanitized) > 100:
            raise ValueError('Breed name cannot exceed 100 characters')
        
        return sanitized
    
    @staticmethod
    def validate_age_format(age: Optional[str]) -> Optional[str]:
        """Validate age format"""
        if age is None:
            return age
        
        age_lower = age.lower().strip()
        valid_units = ['year', 'month', 'week', 'day']
        
        if not any(unit in age_lower for unit in valid_units):
            raise ValueError('Age must include time unit (e.g., "2 years", "6 months")')
        
        # Extract number and validate
        import re
        number_match = re.search(r'(\d+)', age_lower)
        if number_match:
            number = int(number_match.group(1))
            if number <= 0 or number > 30:  # Reasonable age limits
                raise ValueError('Age must be between 1 and 30')
        
        return age_lower
    
    @staticmethod
    def validate_weight_range(weight: Optional[float]) -> Optional[float]:
        """Validate weight range"""
        if weight is None:
            return weight
        
        if weight <= 0:
            raise ValueError('Weight must be greater than 0')
        if weight > 200:  # 200 kg is extremely heavy for a dog
            raise ValueError('Weight cannot exceed 200 kg')
        
        return weight
    
    @staticmethod
    def validate_gender_value(gender: Optional[str]) -> Optional[str]:
        """Validate gender value"""
        if gender is None:
            return gender
        
        valid_genders = ['male', 'female', 'unknown', 'm', 'f']
        normalized = gender.lower().strip()
        
        if normalized not in valid_genders:
            raise ValueError('Gender must be one of: male, female, unknown, m, f')
        
        # Normalize to full form
        if normalized == 'm':
            return 'male'
        elif normalized == 'f':
            return 'female'
        
        return normalized


# Export commonly used validators
__all__ = [
    "ValidationUtils",
    "AssessmentValidators", 
    "VideoValidators",
    "BusinessRuleValidators",
    "CustomValidators"
]
