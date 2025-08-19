import anthropic
import json
from typing import Dict, List, Optional
import os
from dataclasses import dataclass

@dataclass
class DogPersonalityProfile:
    """Structured personality data for Claude API"""
    dog_name: str
    factor_scores: Dict[str, float]
    bias_indicators: Dict[str, float]
    personality_profile: Dict[str, str]
    breed: Optional[str] = None
    age: Optional[str] = None

class ClaudeRecommendationGenerator:
    """
    Generate personalized dog training and care recommendations using Claude API
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize with Claude API key
        
        Args:
            api_key: Anthropic API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Claude API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_recommendations(self, personality_data: Dict) -> Dict[str, List[str]]:
        """
        Generate personalized recommendations using Claude API
        
        Args:
            personality_data: Dictionary containing DPQ results and dog info
            
        Returns:
            Dictionary with categorized recommendations
        """
        try:
            # Create structured prompt for Claude
            user_prompt = self._create_recommendation_prompt(personality_data)
            
            # System prompt for recommendations
            system_prompt = """You are a professional dog behaviorist and trainer specializing in personalized dog care recommendations. 

    Based on Dog Personality Questionnaire (DPQ) results, provide specific, actionable recommendations. Always format your response as valid JSON with exactly these keys: training_tips, exercise_needs, socialization, daily_care, ai_communication.

    Make recommendations specific to the individual dog's personality profile. Avoid generic advice."""
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=[
                    {
                        "type": "text", 
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            # Parse Claude's response
            recommendations = self._parse_claude_response(message.content[0].text)
            return recommendations
            
        except Exception as e:
            print(f"Error generating Claude recommendations: {e}")
            return self._fallback_recommendations()
    
    def _create_recommendation_prompt(self, personality_data: Dict) -> str:
        """Create a detailed prompt for Claude based on personality data"""
        
        dog_name = personality_data.get('dog_info', {}).get('name', 'this dog')
        breed = personality_data.get('dog_info', {}).get('breed', 'Unknown breed')
        
        # Extract key personality insights
        factor_scores = personality_data.get('factor_scores', {})
        bias_indicators = personality_data.get('bias_indicators', {})
        
        prompt = f"""You are a professional dog behaviorist and trainer. Based on the Dog Personality Questionnaire (DPQ) results below, provide personalized recommendations for {dog_name}, a {breed}.

PERSONALITY ASSESSMENT RESULTS:

Dog Information:
- Name: {dog_name}
- Breed: {breed}

Personality Factor Scores (1-7 scale, where 4 is neutral):
"""
        
        # Add factor scores with interpretations
        for factor, score in factor_scores.items():
            level = "High" if score >= 5.5 else "Moderate" if score >= 4.5 else "Low"
            prompt += f"- {factor}: {score:.1f} ({level})\n"
        
        prompt += f"""
Key Behavioral Indicators (0-1 scale):
"""
        
        # Add most relevant bias indicators
        key_indicators = [
            'fearfulness_bias', 'aggression_bias', 'excitability_bias',
            'trainability_bias', 'social_confidence', 'activity_level'
        ]

        for indicator in key_indicators:
            if indicator in bias_indicators:
                value = bias_indicators[indicator]
                level = "High" if value >= 0.7 else "Moderate" if value >= 0.4 else "Low"
                prompt += f"- {indicator.replace('_', ' ').title()}: {value:.2f} ({level})\n"

        # Debug: Add all available indicators if none of the key ones were found
        if not any(indicator in bias_indicators for indicator in key_indicators):
            prompt += "\nAll available indicators:\n"
            for indicator, value in bias_indicators.items():
                level = "High" if value >= 0.7 else "Moderate" if value >= 0.4 else "Low"
                prompt += f"- {indicator.replace('_', ' ').title()}: {value:.2f} ({level})\n"
                
        prompt += f"""

Please provide specific, actionable recommendations in the following categories. Format your response as JSON with these exact keys:

{{
  "training_tips": [
    "Specific training advice based on personality",
    "Methods that work best for this personality type",
    "Training challenges to watch for"
  ],
  "exercise_needs": [
    "Exercise recommendations based on activity level",
    "Types of physical activities that suit this dog",
    "Mental stimulation suggestions"
  ],
  "socialization": [
    "Social interaction recommendations",
    "How to handle social situations",
    "Building confidence tips"
  ],
  "daily_care": [
    "Daily routine suggestions",
    "Environmental considerations",
    "Stress management tips"
  ],
  "ai_communication": [
    "How AI should communicate with this dog's personality",
    "Tone and approach recommendations for AI translation",
    "Behavioral interpretation guidelines for AI"
  ]
}}

Make recommendations specific to this dog's personality profile. Avoid generic advice - focus on what makes this dog unique based on the DPQ results."""

        return prompt
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, List[str]]:
        """Parse Claude's JSON response into structured recommendations"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                recommendations = json.loads(json_str)
                
                # Validate structure
                expected_keys = ['training_tips', 'exercise_needs', 'socialization', 'daily_care', 'ai_communication']
                for key in expected_keys:
                    if key not in recommendations:
                        recommendations[key] = []
                
                return recommendations
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            print(f"Raw response: {response_text[:500]}...")
            return self._fallback_recommendations()
    
    def _fallback_recommendations(self) -> Dict[str, List[str]]:
        """Fallback recommendations if Claude API fails"""
        return {
            "training_tips": [
                "API temporarily unavailable - using basic recommendations",
                "Consult with a professional dog trainer for personalized advice"
            ],
            "exercise_needs": [
                "Provide regular daily exercise appropriate for breed and age",
                "Include both physical and mental stimulation"
            ],
            "socialization": [
                "Gradual exposure to new experiences",
                "Positive reinforcement for calm behavior"
            ],
            "daily_care": [
                "Maintain consistent daily routines",
                "Monitor for signs of stress or anxiety"
            ],
            "ai_communication": [
                "Use calm, consistent communication patterns",
                "Adapt based on individual dog responses"
            ]
        }

# Integration function for your existing code
def replace_hardcoded_recommendations(dpq_results_dict: Dict, dog_info: Dict, api_key: str = None) -> Dict[str, List[str]]:
    """
    Replace hardcoded recommendations with Claude API-generated ones
    
    Args:
        dpq_results_dict: DPQ results dictionary
        dog_info: Dog information dictionary
        api_key: Claude API key (optional if set in environment)
    
    Returns:
        Dictionary with AI-generated recommendations
    """
    try:
        # Initialize Claude recommender
        recommender = ClaudeRecommendationGenerator(api_key=api_key)
        
        # Prepare personality data
        personality_data = {
            'dog_info': dog_info,
            'factor_scores': dpq_results_dict.get('factor_scores', {}),
            'bias_indicators': dpq_results_dict.get('bias_indicators', {}),
            'personality_profile': dpq_results_dict.get('personality_profile', {})
        }
        
        # Generate recommendations
        recommendations = recommender.generate_recommendations(personality_data)
        
        # Convert to format expected by your existing code
        formatted_recommendations = {
            'training_tips': recommendations.get('training_tips', []),
            'exercise_needs': recommendations.get('exercise_needs', []),
            'socialization_tips': recommendations.get('socialization', []),
            'daily_care_tips': recommendations.get('daily_care', []),
            'ai_communication_guidelines': recommendations.get('ai_communication', [])
        }
        
        return formatted_recommendations
        
    except Exception as e:
        print(f"Error generating Claude recommendations: {e}")
        return {
            'training_tips': ["API error - please try again later"],
            'exercise_needs': ["Consult with veterinarian for exercise recommendations"],
            'socialization_tips': ["Work with professional trainer for socialization guidance"],
            'daily_care_tips': ["Maintain consistent routines and monitor dog's wellbeing"],
            'ai_communication_guidelines': ["Use gentle, consistent communication approaches"]
        }

