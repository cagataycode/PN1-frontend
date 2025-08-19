#!/usr/bin/env python3
"""
Test suite for Claude API recommendation generator
Tests both with and without API key to ensure fallback functionality
"""

import os
import json
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, trying to load from system environment")

# Add the parent directory (project root) to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # This goes up to /workspace/PN1.pwa
sys.path.insert(0, parent_dir)

try:
    from dpq.claude_recommender import ClaudeRecommendationGenerator, replace_hardcoded_recommendations
    print("✓ Successfully imported claude_recommender module")
except ImportError as e:
    print(f"❌ Failed to import from dpq.claude_recommender: {e}")
    print("Make sure dpq/claude_recommender.py exists and dpq module is importable")
    sys.exit(1)


class TestClaudeRecommender:
    """Test class for Claude API recommendation functionality"""
    
    def __init__(self):
        self.test_personality_data = {
            'dog_info': {
                'name': 'Bella',
                'breed': 'Border Collie',
                'birthday': '2021-05-15T00:00:00Z'
            },
            'factor_scores': {
                'Factor 1 - Fearfulness': 3.2,
                'Factor 2 - Aggression towards People': 2.1,
                'Factor 3 - Activity/Excitability': 6.4,
                'Factor 4 - Responsiveness to Training': 6.8,
                'Factor 5 - Aggression towards Animals': 3.5
            },
            'bias_indicators': {
                'fearfulness_bias': 0.31,
                'aggression_bias': 0.25,
                'excitability_bias': 0.85,
                'trainability_bias': 0.91,
                'social_confidence': 0.72,
                'dog_sociability': 0.68,
                'environmental_adaptability': 0.75,
                'handling_tolerance': 0.80,
                'attention_seeking': 0.78,
                'activity_level': 0.88,
                'impulse_control': 0.45,
                'territorial_tendency': 0.35,
                'resource_guarding': 0.20,
                'prey_drive': 0.65
            },
            'personality_profile': {
                'Factor 1 - Fearfulness': 'Low',
                'Factor 2 - Aggression towards People': 'Low', 
                'Factor 3 - Activity/Excitability': 'High',
                'Factor 4 - Responsiveness to Training': 'High',
                'Factor 5 - Aggression towards Animals': 'Moderate',
                'Dominant_Traits': 'Energetic/Excitable, Trainable/Responsive'
            }
        }
        
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test results"""
        if passed:
            print(f"✓ {test_name}")
            self.test_results['passed'] += 1
        else:
            print(f"❌ {test_name}: {message}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        try:
            # Temporarily remove API key from environment
            original_key = os.environ.get('ANTHROPIC_API_KEY')
            if 'ANTHROPIC_API_KEY' in os.environ:
                del os.environ['ANTHROPIC_API_KEY']
            
            try:
                recommender = ClaudeRecommendationGenerator()
                self.log_test("Initialization without API key", False, "Should have raised ValueError")
            except ValueError as e:
                if "API key required" in str(e):
                    self.log_test("Initialization without API key", True)
                else:
                    self.log_test("Initialization without API key", False, f"Wrong error message: {e}")
            except Exception as e:
                self.log_test("Initialization without API key", False, f"Unexpected error: {e}")
            
            # Restore original API key
            if original_key:
                os.environ['ANTHROPIC_API_KEY'] = original_key
                
        except Exception as e:
            self.log_test("Initialization without API key", False, f"Test setup error: {e}")
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        try:
            recommender = ClaudeRecommendationGenerator(api_key="test_key_123")
            self.log_test("Initialization with API key", True)
        except Exception as e:
            self.log_test("Initialization with API key", False, str(e))
    
    def test_prompt_creation(self):
        """Test prompt creation functionality"""
        try:
            recommender = ClaudeRecommendationGenerator(api_key="test_key")
            prompt = recommender._create_recommendation_prompt(self.test_personality_data)
            
            print(f"\nDEBUG: Prompt contains 'excitability_bias': {'excitability_bias' in prompt}")
            print(f"DEBUG: Available bias indicators: {list(self.test_personality_data.get('bias_indicators', {}).keys())}")
            
            # Check if prompt contains key elements
            checks = [
                ("Dog name", "Bella" in prompt),
                ("Breed", "Border Collie" in prompt), 
                ("Factor scores", "Factor 1 - Fearfulness: 3.2" in prompt),
                ("High activity", "High" in prompt and "Activity/Excitability" in prompt),
                ("JSON format", "training_tips" in prompt),
                ("Behavioral indicators", "Excitability Bias" in prompt)
            ]
            
            all_passed = True
            for check_name, condition in checks:
                print(f"DEBUG: {check_name}: {condition}")
                if not condition:
                    self.log_test(f"Prompt creation - {check_name}", False, "Missing from prompt")
                    all_passed = False
            
            if all_passed:
                self.log_test("Prompt creation", True)
                print(f"    Prompt length: {len(prompt)} characters")
                
        except Exception as e:
            self.log_test("Prompt creation", False, str(e))

    def test_response_parsing_valid_json(self):
        """Test parsing valid JSON response"""
        try:
            recommender = ClaudeRecommendationGenerator(api_key="test_key")
            
            # Mock valid Claude response
            mock_response = """Here are my recommendations:
            
{
  "training_tips": [
    "Use positive reinforcement with high-energy activities",
    "Channel excitability into structured training sessions"
  ],
  "exercise_needs": [
    "Provide 2+ hours of vigorous exercise daily",
    "Include mental stimulation through puzzle games"
  ],
  "socialization": [
    "Continue positive social experiences",
    "Use controlled environments for new introductions"
  ],
  "daily_care": [
    "Maintain consistent high-energy routines",
    "Provide adequate rest periods between activities"
  ],
  "ai_communication": [
    "Use enthusiastic, energetic communication style",
    "Expect quick responses and high engagement"
  ]
}

These recommendations are based on the high activity and trainability scores."""
            
            parsed = recommender._parse_claude_response(mock_response)
            
            # Validate structure
            expected_keys = ['training_tips', 'exercise_needs', 'socialization', 'daily_care', 'ai_communication']
            all_keys_present = all(key in parsed for key in expected_keys)
            
            if all_keys_present and len(parsed['training_tips']) > 0:
                self.log_test("Response parsing - Valid JSON", True)
                print(f"    Parsed {len(parsed)} categories successfully")
            else:
                self.log_test("Response parsing - Valid JSON", False, "Missing keys or empty content")
                
        except Exception as e:
            self.log_test("Response parsing - Valid JSON", False, str(e))
    
    def test_response_parsing_invalid_json(self):
        """Test parsing invalid JSON response (should use fallback)"""
        try:
            recommender = ClaudeRecommendationGenerator(api_key="test_key")
            
            # Mock invalid response
            invalid_response = "I think your dog needs exercise and training, but I can't format this as JSON properly..."
            
            parsed = recommender._parse_claude_response(invalid_response)
            
            # Should return fallback recommendations
            if 'training_tips' in parsed and 'API temporarily unavailable' in str(parsed['training_tips']):
                self.log_test("Response parsing - Invalid JSON fallback", True)
            else:
                self.log_test("Response parsing - Invalid JSON fallback", False, "Fallback not triggered properly")
                
        except Exception as e:
            self.log_test("Response parsing - Invalid JSON fallback", False, str(e))
    
    @patch('anthropic.Anthropic')
    def test_api_call_success(self, mock_anthropic):
        """Test successful API call with mocked response"""
        try:
            # Mock the Anthropic client and response
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            
            # Mock successful response
            mock_message = MagicMock()
            mock_message.content = [MagicMock()]
            mock_message.content[0].text = """{
  "training_tips": ["Mocked training tip for high-energy Border Collie"],
  "exercise_needs": ["Mocked exercise recommendation"],
  "socialization": ["Mocked socialization advice"],
  "daily_care": ["Mocked daily care tip"],
  "ai_communication": ["Mocked AI communication guideline"]
}"""
            
            mock_client.messages.create.return_value = mock_message
            
            # Test the API call
            recommender = ClaudeRecommendationGenerator(api_key="test_key")
            recommendations = recommender.generate_recommendations(self.test_personality_data)
            
            # Verify the call was made with correct parameters
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args
            
            # Check if the call included the right model and parameters
            if (call_args[1]['model'] == "claude-sonnet-4-20250514" and
                call_args[1]['max_tokens'] == 4000 and
                'system' in call_args[1] and
                'Bella' in call_args[1]['messages'][0]['content']):
                self.log_test("API call success (mocked)", True)
                print(f"    Generated {len(recommendations)} recommendation categories")
            else:
                self.log_test("API call success (mocked)", False, "Incorrect API call parameters")

                
        except Exception as e:
            self.log_test("API call success (mocked)", False, str(e))
    
    @patch('anthropic.Anthropic')
    def test_api_call_failure(self, mock_anthropic):
        """Test API call failure and fallback"""
        try:
            # Mock the Anthropic client to raise an exception
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = Exception("API rate limit exceeded")
            
            # Test the API call
            recommender = ClaudeRecommendationGenerator(api_key="test_key")
            recommendations = recommender.generate_recommendations(self.test_personality_data)
            
            # Should return fallback recommendations
            if ('training_tips' in recommendations and 
                'API temporarily unavailable' in str(recommendations['training_tips'])):
                self.log_test("API call failure fallback", True)
            else:
                self.log_test("API call failure fallback", False, "Fallback not working properly")
                
        except Exception as e:
            self.log_test("API call failure fallback", False, str(e))
    
    def test_integration_function(self):
        """Test the integration function replace_hardcoded_recommendations"""
        try:
            # Test without API key (should use fallback)
            original_key = os.environ.get('ANTHROPIC_API_KEY')
            if 'ANTHROPIC_API_KEY' in os.environ:
                del os.environ['ANTHROPIC_API_KEY']
            
            recommendations = replace_hardcoded_recommendations(
                self.test_personality_data,
                self.test_personality_data['dog_info']
            )
            
            # Should return error recommendations
            expected_keys = ['training_tips', 'exercise_needs', 'socialization_tips', 
                           'daily_care_tips', 'ai_communication_guidelines']
            
            if all(key in recommendations for key in expected_keys):
                self.log_test("Integration function", True)
                print(f"    Returned {len(recommendations)} recommendation categories")
            else:
                self.log_test("Integration function", False, "Missing expected keys")
            
            # Restore API key
            if original_key:
                os.environ['ANTHROPIC_API_KEY'] = original_key
                
        except Exception as e:
            self.log_test("Integration function", False, str(e))
    
    def test_different_personality_profiles(self):
        """Test with different personality profiles"""
        try:
            recommender = ClaudeRecommendationGenerator(api_key="test_key")
            
            # Test with fearful dog
            fearful_dog_data = {
                'dog_info': {'name': 'Shy Sam', 'breed': 'Rescue Mix'},
                'factor_scores': {
                    'Factor 1 - Fearfulness': 6.5,
                    'Factor 2 - Aggression towards People': 2.0,
                    'Factor 3 - Activity/Excitability': 2.8,
                    'Factor 4 - Responsiveness to Training': 3.2,
                    'Factor 5 - Aggression towards Animals': 1.5
                },
                'bias_indicators': {
                    'fearfulness_bias': 0.85,
                    'social_confidence': 0.15,
                    'activity_level': 0.25
                }
            }
            
            prompt = recommender._create_recommendation_prompt(fearful_dog_data)
            
            # Check if prompt adapts to fearful personality
            if "6.5 (High)" in prompt and "Fearfulness Bias" in prompt:
                self.log_test("Different personality profiles", True)
                print("    Prompt correctly adapted for fearful dog profile")
            else:
                self.log_test("Different personality profiles", False, "Prompt didn't adapt to personality")
                
        except Exception as e:
            self.log_test("Different personality profiles", False, str(e))
    
    def test_real_api_call(self):
        """Test actual Claude API call (requires API key)"""
        try:
            # Check if API key is available
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                self.log_test("Real API call", False, "ANTHROPIC_API_KEY not set - skipping real API test")
                return
            
            print(f"\n🔥 Making real API call to Claude...")
            
            # Make real API call
            recommender = ClaudeRecommendationGenerator(api_key=api_key)
            recommendations = recommender.generate_recommendations(self.test_personality_data)
            
            # Validate response structure
            expected_keys = ['training_tips', 'exercise_needs', 'socialization', 'daily_care', 'ai_communication']
            all_keys_present = all(key in recommendations for key in expected_keys)
            
            # Check that we got real recommendations (not fallback)
            has_real_content = (len(recommendations['training_tips']) > 0 and 
                            'API temporarily unavailable' not in str(recommendations['training_tips']))
            
            if all_keys_present and has_real_content:
                self.log_test("Real API call", True)
                print(f"    ✨ Generated real recommendations for {self.test_personality_data['dog_info']['name']}")
                print(f"    📝 Training tip: {recommendations['training_tips'][0][:80]}...")
                print(f"    🏃 Exercise tip: {recommendations['exercise_needs'][0][:80]}...")
            else:
                self.log_test("Real API call", False, "Invalid response structure or fallback triggered")
                
        except Exception as e:
            self.log_test("Real API call", False, str(e))
    def display_full_recommendations(self):
        """Display full Claude recommendations for review"""
        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                print("❌ No API key available for full recommendation display")
                return
                
            print("\n" + "=" * 80)
            print("🐕 FULL CLAUDE RECOMMENDATIONS FOR BELLA")
            print("=" * 80)
            
            recommender = ClaudeRecommendationGenerator(api_key=api_key)
            recommendations = recommender.generate_recommendations(self.test_personality_data)
            
            categories = {
                'training_tips': '🎯 TRAINING TIPS',
                'exercise_needs': '🏃 EXERCISE NEEDS', 
                'socialization': '🤝 SOCIALIZATION',
                'daily_care': '🏠 DAILY CARE',
                'ai_communication': '🤖 AI COMMUNICATION'
            }
            
            for key, title in categories.items():
                print(f"\n{title}")
                print("-" * len(title))
                if key in recommendations:
                    for i, tip in enumerate(recommendations[key], 1):
                        print(f"{i}. {tip}")
                else:
                    print("No recommendations available")
                    
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"❌ Error displaying recommendations: {e}")

    def run_all_tests(self):
        """Run all tests and display results"""
        print("=" * 60)
        print("CLAUDE RECOMMENDER TEST SUITE")
        print("=" * 60)
        print(f"Testing with sample dog: {self.test_personality_data['dog_info']['name']}")
        print(f"Personality: {self.test_personality_data['personality_profile']['Dominant_Traits']}")
        print()
        
        # Run all tests
        self.test_initialization_without_api_key()
        self.test_initialization_with_api_key()
        self.test_prompt_creation()
        self.test_response_parsing_valid_json()
        self.test_response_parsing_invalid_json()
        self.test_api_call_success()
        self.test_api_call_failure()
        self.test_integration_function()
        self.test_different_personality_profiles()
        self.test_real_api_call()

        
        # Display results
        print()
        print("=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"✓ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"Total: {self.test_results['passed'] + self.test_results['failed']}")
        
        if self.test_results['failed'] > 0:
            print("\nFailed tests:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.test_results['passed'] / 
                       (self.test_results['passed'] + self.test_results['failed']) * 100)
        print(f"\nSuccess rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 Claude recommender is working well!")
            print("\nNext steps:")
            print("1. Set your ANTHROPIC_API_KEY environment variable")
            print("2. Test with real API calls")
            print("3. Integrate with your DPQ system")
            
            # Display full recommendations if tests passed
            self.display_full_recommendations()
        else:
            print("\n⚠️  Some tests failed - check the errors above")

        return success_rate >= 80

def main():
    """Run the test suite"""
    print("Starting Claude Recommender Tests...\n")
    
    # Run tests
    tester = TestClaudeRecommender()
    success = tester.run_all_tests()
    
    # Additional info
    print("\n" + "=" * 60)
    print("INTEGRATION NOTES")
    print("=" * 60)
    print("To use Claude API recommendations in your DPQ system:")
    print("\n1. Environment setup:")
    print("   export ANTHROPIC_API_KEY='your_api_key_here'")
    print("\n2. Replace in response_formatter.py:")
    print("   from claude_recommender import replace_hardcoded_recommendations")
    print("\n3. Update _generate_recommendations method:")
    print("   return replace_hardcoded_recommendations(dpq_results, dog_info)")
    print("\n4. Test with real personality data!")
    
    return success

if __name__ == "__main__":
    main()
