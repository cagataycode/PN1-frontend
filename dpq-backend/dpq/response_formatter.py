# response_formatter.py - Convert DPQ results to frontend JSON format

import json
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
from claude_recommender import replace_hardcoded_recommendations

class DPQResponseFormatter:
    """
    Formats DPQ assessment results into the JSON format expected by frontend
    """
    
    def __init__(self):
        self.personality_type_mapping = {
            # Based on dominant traits combinations
            ("high_energy", "high_trainability"): "High-Energy Companion",
            ("high_energy", "low_trainability"): "Independent Adventurer", 
            ("low_energy", "high_trainability"): "Calm Companion",
            ("low_energy", "low_trainability"): "Laid-Back Independent",
            ("high_fearfulness", "high_trainability"): "Sensitive Learner",
            ("high_fearfulness", "low_trainability"): "Anxious Independent",
            ("high_aggression", "high_energy"): "Assertive Guardian",
            ("moderate", "moderate"): "Balanced Companion"
        }
    
    def format_assessment_response(self, 
                                 dpq_results: Dict[str, Any],
                                 dog_info: Dict[str, Any],
                                 user_id: str,
                                 assessment_metadata: Dict[str, Any],
                                 responses: Dict[str, int]) -> Dict[str, Any]:
        """
        Convert DPQ results to complete frontend JSON format
        
        Args:
            dpq_results: Output from DPQ.score_assessment()
            dog_info: Dog information from request
            user_id: User UUID
            assessment_metadata: Timing and device info
            responses: Raw 1-7 scale responses
            
        Returns:
            Complete JSON response for frontend
        """
        
        # Generate assessment ID
        assessment_id = str(uuid.uuid4())
        dog_id = dog_info.get('dog_id', str(uuid.uuid4()))
        
        # Format personality factors
        personality_factors = self._format_personality_factors(dpq_results['factor_scores'])
        
        # Generate AI bias indicators (this is critical for AI translator)
        ai_bias_indicators = self._format_ai_bias_indicators(dpq_results['bias_indicators'])
        
        # Generate personality summary
        personality_summary = self._generate_personality_summary(personality_factors)
        
        # Generate AI translator config
        ai_translator_config = self._generate_ai_translator_config(ai_bias_indicators)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(personality_factors, ai_bias_indicators, dog_info)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(responses, dpq_results)
        
        # Build complete response
        response = {
            # Database IDs
            "assessment_id": assessment_id,
            "dog_id": dog_id,
            "user_id": user_id,
            
            # Assessment timing (matches dpq_assessments table)
            "started_at": assessment_metadata.get('started_at'),
            "completed_at": assessment_metadata.get('completed_at'),
            "assessment_duration_minutes": assessment_metadata.get('assessment_duration_minutes'),
            "device_type": assessment_metadata.get('device_type'),
            "app_version": assessment_metadata.get('app_version'),
            
            # Dog information (from dogs table)
            "dog_info": self._format_dog_info(dog_info),
            
            # Raw responses (stored in dpq_assessments.responses JSONB)
            "responses": {str(k): v for k, v in responses.items()},
            
            # Personality factors (stored in dpq_assessments.personality_factors JSONB)
            "personality_factors": personality_factors,
            
            # AI bias indicators (stored in dpq_assessments.ai_bias_indicators JSONB)
            # CRITICAL FOR AI TRANSLATOR CALIBRATION
            "ai_bias_indicators": ai_bias_indicators,
            
            # Personality summary (stored in dpq_assessments.personality_summary JSONB)
            "personality_summary": personality_summary,
            
            # AI translator config (stored in dpq_assessments.ai_translator_config JSONB)
            "ai_translator_config": ai_translator_config,
            
            # Recommendations (stored in dpq_assessments.recommendations JSONB)
            "recommendations": recommendations,
            
            # Assessment quality metrics (stored in dpq_assessments table)
            "quality_metrics": quality_metrics,
            
            # Versioning (stored in dpq_assessments table)
            "metadata": {
                "assessment_version": "DPQ_Short_Form_v1.0",
                "scoring_algorithm": "Jones_2009_validated",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        return response
    
    def _format_personality_factors(self, factor_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Format personality factors with levels and descriptions
        """
        factors = {}
        
        for factor_name, score in factor_scores.items():
            level = self._get_level_from_score(score)
            
            factors[factor_name] = {
                "score": round(score, 1),
                "level": level,
                "description": self._get_factor_description(factor_name, level),
            }
        
        return factors
    
    def _format_ai_bias_indicators(self, bias_indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Format AI bias indicators (0-1 scale) - CRITICAL FOR AI TRANSLATOR
        """
        # Ensure all values are between 0 and 1
        formatted_indicators = {}
        for key, value in bias_indicators.items():
            formatted_indicators[key] = max(0.0, min(1.0, round(value, 2)))
        
        return formatted_indicators
    
    def _generate_personality_summary(self, personality_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate human-readable personality summary
        """
        # Identify dominant traits
        dominant_traits = []
        high_factors = []
        
        for factor_name, factor_data in personality_factors.items():
            if factor_data['level'] == 'High':
                high_factors.append(factor_name)
                if factor_name == 'activity_excitability':
                    dominant_traits.append('Energetic/Excitable')
                elif factor_name == 'training_responsiveness':
                    dominant_traits.append('Trainable/Responsive')
                elif factor_name == 'fearfulness':
                    dominant_traits.append('Sensitive/Cautious')
        
        # Determine primary personality type
        primary_type = self._determine_primary_type(high_factors)
        
        # Generate key characteristics
        key_characteristics = self._generate_key_characteristics(personality_factors)
        
        return {
            "dominant_traits": dominant_traits[:2],  # Top 2 traits
            "primary_type": primary_type,
            "key_characteristics": key_characteristics
        }
    
    def _generate_ai_translator_config(self, ai_bias_indicators: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate AI translator configuration based on bias indicators
        """
        # Determine communication style
        excitability = ai_bias_indicators.get('excitability_bias', 0.5)
        fearfulness = ai_bias_indicators.get('fearfulness_bias', 0.5)
        trainability = ai_bias_indicators.get('trainability_bias', 0.5)
        
        if excitability > 0.7:
            communication_style = "energetic_friendly"
        elif fearfulness > 0.7:
            communication_style = "calm_reassuring"
        elif trainability > 0.7:
            communication_style = "structured_positive"
        else:
            communication_style = "balanced_adaptive"
        
        return {
            "communication_style": communication_style,
            "tone_adjustments": {
                "base_energy_level": "high" if excitability > 0.6 else "moderate",
                "excitement_threshold": round(excitability, 2),
                "calming_needed": fearfulness > 0.6,
                "authority_response": "positive" if trainability > 0.6 else "gentle"
            },
            "response_modifications": {
                "increase_enthusiasm": round(excitability, 2),
                "add_training_cues": round(trainability, 2),
                "reduce_fear_language": round(1.0 - fearfulness, 2),
                "enhance_play_references": round(excitability * 0.8, 2)
            }
        }
    
    def _generate_recommendations(self, personality_factors: Dict[str, Any],
                                ai_bias_indicators: Dict[str, float],
                                dog_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommendations using Claude API
        """
        try:
            # Prepare data for Claude API
            dpq_results_dict = {
                'factor_scores': {name: data['score'] for name, data in personality_factors.items()},
                'bias_indicators': ai_bias_indicators,
                'personality_profile': {name: data['level'] for name, data in personality_factors.items()}
            }
            
            # Use actual dog info instead of placeholder
            claude_dog_info = {
                'name': dog_info.get('name', 'this dog'),
                'breed': dog_info.get('breed', 'Unknown breed'),
                'age': dog_info.get('age_years', 'Unknown age')
            }
            
            # Get Claude recommendations
            claude_recommendations = replace_hardcoded_recommendations(dpq_results_dict, claude_dog_info)
            
            return {
                "training_tips": claude_recommendations.get('training_tips', []),
                "exercise_needs": claude_recommendations.get('exercise_needs', []),
                "ai_translator_tips": claude_recommendations.get('ai_communication_guidelines', [])
            }
            
        except Exception as e:
            print(f"Error generating Claude recommendations: {e}")
            return {
                "training_tips": ["Recommendations temporarily unavailable"],
                "exercise_needs": ["Recommendations temporarily unavailable"], 
                "ai_translator_tips": ["Recommendations temporarily unavailable"]
            }
   
    def _calculate_quality_metrics(self, responses: Dict[str, int], 
                                 dpq_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate assessment quality metrics
        """
        # Check for extreme response bias (all 1s, all 7s, etc.)
        values = list(responses.values())
        unique_values = set(values)
        extreme_bias = len(unique_values) <= 2
        
        # Calculate response consistency (mock implementation)
        consistency = "high" if len(unique_values) >= 4 else "low"
        
        return {
            "reliability_score": 0.94,  # Mock score - would be calculated from actual data
            "response_consistency": consistency,
            "extreme_response_bias": extreme_bias,
            "all_questions_answered": len(responses) == 45
        }
    
    def _format_dog_info(self, dog_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format dog information with calculated age
        """
        formatted_info = dog_info.copy()
        
        # Calculate age if birthday is provided
        if 'birthday' in dog_info and dog_info['birthday']:
            try:
                birthday = datetime.fromisoformat(dog_info['birthday'].replace('Z', '+00:00'))
                age_years = (datetime.now() - birthday).days // 365
                formatted_info['age_years'] = age_years
            except:
                formatted_info['age_years'] = None
        
        # Add created_at if not present
        if 'created_at' not in formatted_info:
            formatted_info['created_at'] = datetime.utcnow().isoformat() + "Z"
        
        return formatted_info
    
    def _get_level_from_score(self, score: float) -> str:
        """
        Convert numeric score to level description
        """
        if score >= 5.5:
            return "High"
        elif score >= 4.5:
            return "Moderate-High"
        elif score >= 3.5:
            return "Moderate"
        elif score >= 2.5:
            return "Moderate-Low"
        else:
            return "Low"
    

    def _get_factor_description(self, factor_name: str, level: str) -> str:
        """
        Get description for personality factor
        """
        descriptions = {
            'fearfulness': {
                'High': 'Shows high levels of anxiety and fear responses',
                'Moderate': 'Shows moderate levels of anxiety and fear responses',
                'Low': 'Generally confident and calm in various situations'
            },
            'aggression_people': {
                'High': 'May show aggressive tendencies toward people',
                'Moderate': 'Shows some wariness or assertiveness with people',
                'Low': 'Generally friendly and non-aggressive toward people'
            },
            'activity_excitability': {
                'High': 'Highly energetic, excitable, and active',
                'Moderate': 'Moderately energetic with balanced activity levels',
                'Low': 'Calm and low-energy, prefers quiet activities'
            },
            'training_responsiveness': {
                'High': 'Highly trainable and responsive to commands',
                'Moderate': 'Moderately trainable with consistent effort',
                'Low': 'May be challenging to train, requires patience'
            },
            'aggression_animals': {
                'High': 'Shows high reactivity or aggression toward other animals',
                'Moderate': 'Shows moderate reactivity toward other animals',
                'Low': 'Generally peaceful and non-aggressive with other animals'
            }
        }
        
        return descriptions.get(factor_name, {}).get(level, f"{level} levels for {factor_name}")
    
    def _determine_primary_type(self, high_factors: list) -> str:
        """
        Determine primary personality type based on high factors
        """
        if 'activity_excitability' in high_factors and 'training_responsiveness' in high_factors:
            return "High-Energy Companion"
        elif 'activity_excitability' in high_factors:
            return "Energetic Explorer"
        elif 'training_responsiveness' in high_factors:
            return "Eager Learner"
        elif 'fearfulness' in high_factors:
            return "Sensitive Soul"
        elif len(high_factors) == 0:
            return "Balanced Companion"
        else:
            return "Unique Personality"
    
    def _generate_key_characteristics(self, personality_factors: Dict[str, Any]) -> list:
        """
        Generate key characteristics based on personality factors
        """
        characteristics = []
        
        for factor_name, factor_data in personality_factors.items():
            level = factor_data['level']
            
            if factor_name == 'activity_excitability' and level == 'High':
                characteristics.append("Very energetic and playful")
            elif factor_name == 'training_responsiveness' and level == 'High':
                characteristics.append("Highly trainable and responsive")
            elif factor_name == 'aggression_people' and level == 'Low':
                characteristics.append("Generally friendly with people")
            elif factor_name == 'fearfulness' and level == 'High':
                characteristics.append("Sensitive and needs gentle handling")
        
        # Add default characteristics if none found
        if not characteristics:
            characteristics.append("Well-balanced personality")
            characteristics.append("Adaptable to various situations")
        
        return characteristics[:5]  # Limit to 5 characteristics