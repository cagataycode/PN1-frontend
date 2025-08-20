"""
Assessment Models - Data structures for DPQ assessment process

This module defines the data models for:
- Assessment requests and responses
- DPQ questionnaire data
- Assessment results and metadata
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from .validation import CustomValidators


class AssessmentStatus(str, Enum):
    """Status of an assessment"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DogInfo(BaseModel):
    """Information about a dog"""
    name: str = Field(..., description="Dog's name", min_length=1, max_length=100)
    breed: Optional[str] = Field(None, description="Dog's breed", max_length=100)
    age: Optional[str] = Field(None, description="Dog's age (e.g., '2 years', '6 months')", max_length=50)
    weight: Optional[float] = Field(None, description="Dog's weight in kg", ge=0, le=200)
    gender: Optional[str] = Field(None, description="Dog's gender", max_length=20)
    owner_name: Optional[str] = Field(None, description="Owner's name", max_length=100)
    
    @validator('name')
    def validate_name(cls, v):
        return CustomValidators.validate_dog_name(v)
    
    @validator('age')
    def validate_age(cls, v):
        return CustomValidators.validate_age_format(v)
    
    @validator('gender')
    def validate_gender(cls, v):
        return CustomValidators.validate_gender_value(v)
    
    @validator('weight')
    def validate_weight(cls, v):
        return CustomValidators.validate_weight_range(v)


class AssessmentRequest(BaseModel):
    """Request model for starting a DPQ assessment"""
    dog_info: DogInfo = Field(..., description="Information about the dog")
    responses: Dict[int, int] = Field(..., description="DPQ responses (question_number: response_value)")
    include_recommendations: bool = Field(True, description="Whether to include AI recommendations")
    include_video_analysis: bool = Field(False, description="Whether to include video analysis")
    
    @validator('responses')
    def validate_responses(cls, v):
        if not v:
            raise ValueError('Responses cannot be empty')
        
        # Check that all responses are valid (1-5 scale)
        valid_values = {1, 2, 3, 4, 5}
        expected_questions = set(range(1, 51))  # DPQ typically has 50 questions
        
        # Validate response format and values
        for question_num, response in v.items():
            if not isinstance(question_num, (int, str)) or not isinstance(response, int):
                raise ValueError('Invalid response format')
            if response not in valid_values:
                raise ValueError(f'Response value {response} must be between 1 and 5')
        
        # Convert string question numbers to integers
        processed_responses = {}
        for question_num, response in v.items():
            if isinstance(question_num, str):
                try:
                    question_num = int(question_num)
                except ValueError:
                    raise ValueError(f'Invalid question number format: {question_num}')
            
            if question_num not in expected_questions:
                raise ValueError(f'Question number {question_num} is not valid (expected 1-50)')
            
            processed_responses[question_num] = response
        
        # Check if we have a reasonable number of responses
        if len(processed_responses) < 30:
            raise ValueError('Assessment must have at least 30 responses to be valid')
        
        return processed_responses


class AssessmentData(BaseModel):
    """Complete assessment data structure"""
    assessment_id: str = Field(..., description="Unique assessment identifier")
    dog_info: DogInfo = Field(..., description="Information about the dog")
    responses: Dict[int, int] = Field(..., description="DPQ responses")
    status: AssessmentStatus = Field(..., description="Current assessment status")
    created_at: datetime = Field(..., description="When the assessment was created")
    updated_at: datetime = Field(..., description="When the assessment was last updated")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class FactorScores(BaseModel):
    """Personality factor scores from DPQ"""
    neuroticism: float = Field(..., description="Neuroticism score", ge=0, le=100)
    extraversion: float = Field(..., description="Extraversion score", ge=0, le=100)
    openness: float = Field(..., description="Openness score", ge=0, le=100)
    agreeableness: float = Field(..., description="Agreeableness score", ge=0, le=100)
    conscientiousness: float = Field(..., description="Conscientiousness score", ge=0, le=100)


class FacetScores(BaseModel):
    """Personality facet scores from DPQ"""
    fear: Optional[float] = Field(None, description="Fear facet score", ge=0, le=100)
    anxiety: Optional[float] = Field(None, description="Anxiety facet score", ge=0, le=100)
    aggression: Optional[float] = Field(None, description="Aggression facet score", ge=0, le=100)
    sociability: Optional[float] = Field(None, description="Sociability facet score", ge=0, le=100)
    activity: Optional[float] = Field(None, description="Activity facet score", ge=0, le=100)
    playfulness: Optional[float] = Field(None, description="Playfulness facet score", ge=0, le=100)
    curiosity: Optional[float] = Field(None, description="Curiosity facet score", ge=0, le=100)
    trainability: Optional[float] = Field(None, description="Trainability facet score", ge=0, le=100)
    affection: Optional[float] = Field(None, description="Affection facet score", ge=0, le=100)
    cooperation: Optional[float] = Field(None, description="Cooperation facet score", ge=0, le=100)


class PersonalityProfile(BaseModel):
    """Personality profile interpretation"""
    neuroticism_profile: str = Field(..., description="Neuroticism profile description")
    extraversion_profile: str = Field(..., description="Extraversion profile description")
    openness_profile: str = Field(..., description="Openness profile description")
    agreeableness_profile: str = Field(..., description="Agreeableness profile description")
    conscientiousness_profile: str = Field(..., description="Conscientiousness profile description")
    overall_profile: str = Field(..., description="Overall personality summary")


class BiasIndicators(BaseModel):
    """Bias indicators in assessment responses"""
    acquiescence: Optional[float] = Field(None, description="Acquiescence bias score", ge=0, le=100)
    social_desirability: Optional[float] = Field(None, description="Social desirability bias score", ge=0, le=100)
    extreme_responding: Optional[float] = Field(None, description="Extreme responding bias score", ge=0, le=100)


class DPQResults(BaseModel):
    """Complete DPQ assessment results"""
    raw_scores: Dict[int, int] = Field(..., description="Raw response scores")
    factor_scores: FactorScores = Field(..., description="Personality factor scores")
    facet_scores: FacetScores = Field(..., description="Personality facet scores")
    personality_profile: PersonalityProfile = Field(..., description="Personality profile interpretation")
    bias_indicators: BiasIndicators = Field(..., description="Bias indicators")
    assessment_metadata: Dict[str, Any] = Field(..., description="Assessment metadata")


class AIRecommendations(BaseModel):
    """AI-generated recommendations"""
    training_tips: List[str] = Field(..., description="Training recommendations")
    exercise_needs: List[str] = Field(..., description="Exercise recommendations")
    socialization: List[str] = Field(..., description="Socialization recommendations")
    daily_care: List[str] = Field(..., description="Daily care recommendations")
    ai_communication: List[str] = Field(..., description="Communication recommendations")
    metadata: Dict[str, Any] = Field(..., description="Recommendation metadata")


class AssessmentResponse(BaseModel):
    """Complete assessment response"""
    assessment_id: str = Field(..., description="Unique assessment identifier")
    status: AssessmentStatus = Field(..., description="Assessment status")
    dog_info: DogInfo = Field(..., description="Dog information")
    dpq_results: DPQResults = Field(..., description="DPQ analysis results")
    ai_recommendations: Optional[AIRecommendations] = Field(None, description="AI recommendations")
    video_analysis: Optional[Dict[str, Any]] = Field(None, description="Video analysis results")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    created_at: datetime = Field(..., description="When the assessment was created")
    processed_at: datetime = Field(..., description="When the assessment was processed")
