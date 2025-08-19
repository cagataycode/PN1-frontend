"""
Dog Models - Data structures for dog information and profiles

This module defines the data models for:
- Dog information and profiles
- Dog behavior data
- Dog owner information
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class DogGender(str, Enum):
    """Dog gender options"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class DogSize(str, Enum):
    """Dog size categories"""
    TOY = "toy"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    GIANT = "giant"


class DogActivityLevel(str, Enum):
    """Dog activity level"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DogInfo(BaseModel):
    """Basic information about a dog"""
    name: str = Field(..., description="Dog's name", min_length=1, max_length=100)
    breed: Optional[str] = Field(None, description="Dog's breed", max_length=100)
    age: Optional[str] = Field(None, description="Dog's age (e.g., '2 years', '6 months')", max_length=50)
    weight: Optional[float] = Field(None, description="Dog's weight in kg", ge=0, le=200)
    gender: Optional[DogGender] = Field(None, description="Dog's gender")
    size: Optional[DogSize] = Field(None, description="Dog's size category")
    activity_level: Optional[DogActivityLevel] = Field(None, description="Dog's activity level")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Dog name cannot be empty')
        return v.strip()


class DogProfile(BaseModel):
    """Complete dog profile with extended information"""
    dog_id: str = Field(..., description="Unique dog identifier")
    basic_info: DogInfo = Field(..., description="Basic dog information")
    owner_name: Optional[str] = Field(None, description="Owner's name", max_length=100)
    owner_email: Optional[str] = Field(None, description="Owner's email", max_length=255)
    owner_phone: Optional[str] = Field(None, description="Owner's phone number", max_length=20)
    
    # Medical information
    medical_conditions: Optional[List[str]] = Field(None, description="List of medical conditions")
    medications: Optional[List[str]] = Field(None, description="List of current medications")
    allergies: Optional[List[str]] = Field(None, description="List of allergies")
    veterinarian: Optional[str] = Field(None, description="Veterinarian name and contact")
    
    # Behavioral information
    training_level: Optional[str] = Field(None, description="Current training level", max_length=100)
    behavioral_issues: Optional[List[str]] = Field(None, description="List of behavioral issues")
    special_needs: Optional[List[str]] = Field(None, description="List of special needs")
    
    # Lifestyle information
    living_environment: Optional[str] = Field(None, description="Living environment (apartment, house, etc.)", max_length=100)
    other_pets: Optional[List[str]] = Field(None, description="Other pets in household")
    children: Optional[str] = Field(None, description="Children in household", max_length=100)
    exercise_routine: Optional[str] = Field(None, description="Current exercise routine", max_length=500)
    
    # Metadata
    created_at: datetime = Field(..., description="When the profile was created")
    updated_at: datetime = Field(..., description="When the profile was last updated")
    profile_complete: bool = Field(False, description="Whether the profile is complete")
    
    class Config:
        schema_extra = {
            "example": {
                "dog_id": "dog_123",
                "basic_info": {
                    "name": "Buddy",
                    "breed": "Golden Retriever",
                    "age": "3 years",
                    "weight": 30.5,
                    "gender": "male",
                    "size": "large",
                    "activity_level": "high"
                },
                "owner_name": "John Smith",
                "owner_email": "john@example.com",
                "medical_conditions": ["None"],
                "training_level": "Intermediate",
                "living_environment": "House with yard",
                "profile_complete": True
            }
        }


class DogBehavior(BaseModel):
    """Dog behavior observations and analysis"""
    dog_id: str = Field(..., description="Unique dog identifier")
    observation_date: datetime = Field(..., description="When the behavior was observed")
    behavior_type: str = Field(..., description="Type of behavior observed", max_length=100)
    description: str = Field(..., description="Detailed description of the behavior", max_length=1000)
    context: Optional[str] = Field(None, description="Context of the behavior", max_length=500)
    intensity: Optional[int] = Field(None, description="Behavior intensity (1-10)", ge=1, le=10)
    duration: Optional[str] = Field(None, description="Duration of the behavior", max_length=100)
    
    # Analysis results
    emotion_primary: Optional[str] = Field(None, description="Primary emotion detected", max_length=50)
    emotion_secondary: Optional[str] = Field(None, description="Secondary emotion detected", max_length=50)
    body_language: Optional[str] = Field(None, description="Body language analysis", max_length=500)
    interpretation: Optional[str] = Field(None, description="Behavior interpretation", max_length=500)
    
    # Metadata
    observer: Optional[str] = Field(None, description="Who observed the behavior", max_length=100)
    confidence: Optional[float] = Field(None, description="Confidence in analysis (0-1)", ge=0, le=1)
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class DogTraining(BaseModel):
    """Dog training information and progress"""
    dog_id: str = Field(..., description="Unique dog identifier")
    training_session_id: str = Field(..., description="Unique training session identifier")
    session_date: datetime = Field(..., description="When the training session occurred")
    duration_minutes: int = Field(..., description="Session duration in minutes", ge=1, le=480)
    
    # Training details
    commands_practiced: List[str] = Field(..., description="Commands practiced during session")
    new_commands_introduced: Optional[List[str]] = Field(None, description="New commands introduced")
    success_rate: float = Field(..., description="Success rate (0-1)", ge=0, le=1)
    
    # Behavioral observations
    focus_level: Optional[int] = Field(None, description="Dog's focus level (1-10)", ge=1, le=10)
    energy_level: Optional[int] = Field(None, description="Dog's energy level (1-10)", ge=1, le=10)
    challenges: Optional[List[str]] = Field(None, description="Challenges encountered")
    breakthroughs: Optional[List[str]] = Field(None, description="Breakthroughs achieved")
    
    # Notes and recommendations
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)
    next_session_goals: Optional[List[str]] = Field(None, description="Goals for next session")
    trainer: Optional[str] = Field(None, description="Trainer name", max_length=100)


class DogHealth(BaseModel):
    """Dog health and medical information"""
    dog_id: str = Field(..., description="Unique dog identifier")
    record_date: datetime = Field(..., description="When the health record was created")
    record_type: str = Field(..., description="Type of health record", max_length=100)
    
    # Vital signs
    weight: Optional[float] = Field(None, description="Weight in kg", ge=0, le=200)
    temperature: Optional[float] = Field(None, description="Temperature in Celsius", ge=35, le=42)
    heart_rate: Optional[int] = Field(None, description="Heart rate (beats per minute)", ge=40, le=200)
    respiratory_rate: Optional[int] = Field(None, description="Respiratory rate (breaths per minute)", ge=10, le=50)
    
    # Health status
    overall_health: Optional[str] = Field(None, description="Overall health status", max_length=100)
    symptoms: Optional[List[str]] = Field(None, description="Current symptoms")
    medications: Optional[List[str]] = Field(None, description="Current medications")
    treatments: Optional[List[str]] = Field(None, description="Current treatments")
    
    # Veterinary information
    veterinarian: Optional[str] = Field(None, description="Veterinarian name", max_length=100)
    clinic: Optional[str] = Field(None, description="Veterinary clinic", max_length=200)
    next_appointment: Optional[datetime] = Field(None, description="Next veterinary appointment")
    
    # Notes
    notes: Optional[str] = Field(None, description="Additional health notes", max_length=1000)
    recommendations: Optional[List[str]] = Field(None, description="Health recommendations")
