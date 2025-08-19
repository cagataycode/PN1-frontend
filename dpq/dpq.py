import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cycler

# Enable grid and update its appearance
plt.rcParams.update({'axes.grid': True})
plt.rcParams.update({'grid.color': 'silver'})
plt.rcParams.update({'grid.linestyle': '--'})

# Set figure resolution
plt.rcParams.update({'figure.dpi': 150})

# Hide the top and right spines
plt.rcParams.update({'axes.spines.top': False})
plt.rcParams.update({'axes.spines.right': False})

# Increase font sizes
plt.rcParams.update({'font.size': 12})  # General font size
plt.rcParams.update({'axes.titlesize': 14})  # Title font size
plt.rcParams.update({'axes.labelsize': 12})  # Axis label font size

plt.rcParams.update({'axes.prop_cycle': cycler.cycler('color', ['#4271FF'])})
import seaborn as sns
from datetime import datetime
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import warnings

warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")


@dataclass
class DPQResults:
    """Data class to store DPQ assessment results"""
    dog_id: str
    assessment_date: str
    raw_scores: Dict[int, int]
    factor_scores: Dict[str, float]
    facet_scores: Dict[str, float]
    personality_profile: Dict[str, str]
    bias_indicators: Dict[str, float]


class DogPersonalityQuestionnaire:
    """
    Dog Personality Questionnaire (DPQ) Short Form Implementation
    Based on Jones, A. C. (2009) - 45 items measuring 5 major personality factors
    """
   
    def __init__(self):
        self.questions = {
            1: "Dog is relaxed when greeting people.",
            2: "Dog behaves aggressively toward dogs.",
            3: "Dog is anxious",
            4: "Dog is lethargic",
            5: "When off leash, dog comes immediately when called.",
            6: "Dog is shy.",
            7: "Dog behaves aggressively towards unfamiliar people.",
            8: "Dog likes to chase squirrels, birds, or other small animals.",
            9: "Dog gets bored in play quickly.",
            10: "Dog is quick to sneak out through open doors, gates.",
            11: "Dog is confident.",
            12: "Dog is dominant over other dogs.",
            13: "Dog avoids other dogs.",
            14: "Dog works at tasks (e.g., getting treats out of a Kong, shredding toys) until entirely finished.",
            15: "Dog is boisterous.",
            16: "Dog behaves fearfully during visits to the veterinarian.",
            17: "Dog enjoys playing with toys.",
            18: "Dog is friendly towards unfamiliar people.",
            19: "Dog is playful with other dogs.",
            20: "Dog seeks companionship from people.",
            21: "Dog behaves submissively (e.g., rolls over, avoids eye contact, licks lips) when greeting other dogs.",
            22: "Dog adapts easily to new situations and environments.",
            23: "Dog likes to chase bicycles, joggers, and skateboarders.",
            24: "Dog is curious.",
            25: "Dog behaves aggressively in response to perceived threats from people (e.g., being cornered, having collar reached for).",
            26: "Dog is aloof.",
            27: "Dog behaves fearfully towards unfamiliar people.",
            28: "Dog willingly shares toys with other dogs.",
            29: "Dog is slow to respond to corrections.",
            30: "Dog behaves aggressively during visits to the veterinarian.",
            31: "Dog seeks constant activity.",
            32: "Dog leaves food or objects alone when told to do so.",
            33: "Dog retrieves objects (e.g., balls, toys, sticks).",
            34: "Dog is friendly towards other dogs.",
            35: "Dog exhibits fearful behaviors when restrained.",
            36: "Dog aggressively guards coveted items (e.g., stolen item, treats, food bowl).",
            37: "Dog is affectionate.",
            38: "Dog ignores commands.",
            39: "Dog behaves aggressively towards cats.",
            40: "Dog shows aggression when nervous or fearful.",
            41: "Dog tends to be calm.",
            42: "Dog behaves fearfully towards other dogs.",
            43: "Dog is able to focus on a task in a distracting situation (e.g., loud or busy places, around other dogs).",
            44: "Dog behaves fearfully when groomed (e.g., nails trimmed, brushed, bathed, ears cleaned).",
            45: "Dog is assertive or pushy with other dogs (e.g., if in a home with other dogs, when greeting)."
        }
       
        # Scoring structure based on official DPQ Short Form
        self.scoring_structure = {
            "Factor 1 - Fearfulness": {
                "Fear of People": {"items": [1, 6, 27], "reverse": [1]},
                "Nonsocial Fear": {"items": [3, 11, 22], "reverse": [11, 22]},
                "Fear of Dogs": {"items": [13, 21, 42], "reverse": []},
                "Fear of Handling": {"items": [16, 35, 44], "reverse": []}
            },
            "Factor 2 - Aggression towards People": {
                "General Aggression": {"items": [7, 18, 40], "reverse": [18]},
                "Situational Aggression": {"items": [25, 30, 36], "reverse": []}
            },
            "Factor 3 - Activity/Excitability": {
                "Excitability": {"items": [15, 31, 41], "reverse": [41]},
                "Playfulness": {"items": [9, 17, 33], "reverse": [9]},
                "Active Engagement": {"items": [4, 14, 24], "reverse": [4]},
                "Companionability": {"items": [20, 26, 37], "reverse": [26]}
            },
            "Factor 4 - Responsiveness to Training": {
                "Trainability": {"items": [29, 38, 43], "reverse": [29, 38]},
                "Controllability": {"items": [5, 10, 32], "reverse": [10]}
            },
            "Factor 5 - Aggression towards Animals": {
                "Aggression towards Dogs": {"items": [2, 19, 34], "reverse": [19, 34]},
                "Prey Drive": {"items": [8, 23, 39], "reverse": []},
                "Dominance over Other Dogs": {"items": [12, 28, 45], "reverse": [28]}
            }
        }
       
        self.scale_labels = {
            1: "Disagree strongly",
            2: "Disagree moderately",
            3: "Disagree slightly",
            4: "Neither agree nor disagree",
            5: "Agree slightly",
            6: "Agree moderately",
            7: "Agree strongly"
        }

    def display_questionnaire(self) -> None:
        """Display the complete questionnaire for manual completion"""
        print("=" * 80)
        print("DOG PERSONALITY QUESTIONNAIRE (DPQ) - SHORT FORM")
        print("=" * 80)
        print("\nHere are personality traits and behavioral descriptions that may or may not")
        print("apply to your dog. Please rate your dog based on his or her general, overall behavior.\n")
       
        print("Rating Scale:")
        for num, label in self.scale_labels.items():
            print(f"  {num} = {label}")
        print("\n" + "=" * 80)
       
        for i, question in self.questions.items():
            print(f"{i:2d}. _____ {question}")
            if i % 10 == 0:  # Add spacing every 10 questions
                print()
       
        print("\n" + "=" * 80)

    def collect_responses(self, dog_id: str = None) -> Dict[int, int]:
        """Collect responses interactively"""
        if not dog_id:
            dog_id = input("Enter dog ID/name: ").strip()
       
        print(f"\nAssessing: {dog_id}")
        print("Please rate each statement (1-7):")
        print("1=Disagree strongly, 4=Neither agree/disagree, 7=Agree strongly\n")
       
        responses = {}
        for i, question in self.questions.items():
            while True:
                try:
                    print(f"{i:2d}. {question}")
                    response = int(input("    Rating (1-7): "))
                    if 1 <= response <= 7:
                        responses[i] = response
                        break
                    else:
                        print("    Please enter a number between 1 and 7")
                except ValueError:
                    print("    Please enter a valid number")
           
            if i % 5 == 0:  # Progress indicator
                print(f"    Progress: {i}/45 questions completed\n")
       
        return responses

    def score_assessment(self, responses: Dict[int, int], dog_id: str = "Unknown") -> DPQResults:
        """Score the DPQ assessment and return comprehensive results"""
       
        # Reverse code items where needed
        processed_responses = responses.copy()
        for factor_name, facets in self.scoring_structure.items():
            for facet_name, facet_info in facets.items():
                for item in facet_info["reverse"]:
                    if item in processed_responses:
                        processed_responses[item] = 8 - processed_responses[item]
       
        # Calculate facet scores
        facet_scores = {}
        for factor_name, facets in self.scoring_structure.items():
            for facet_name, facet_info in facets.items():
                items = facet_info["items"]
                valid_scores = [processed_responses[item] for item in items if item in processed_responses]
                if valid_scores:
                    facet_scores[facet_name] = np.mean(valid_scores)
                else:
                    facet_scores[facet_name] = 4.0  # Neutral if no valid responses
       
        # Calculate factor scores
        factor_scores = {}
        for factor_name, facets in self.scoring_structure.items():
            factor_facets = list(facets.keys())
            valid_facet_scores = [facet_scores[facet] for facet in factor_facets if facet in facet_scores]
            if valid_facet_scores:
                factor_scores[factor_name] = np.mean(valid_facet_scores)
            else:
                factor_scores[factor_name] = 4.0
       
        # Generate personality profile
        personality_profile = self._generate_personality_profile(factor_scores, facet_scores)
       
        # Calculate bias indicators for AI translation
        bias_indicators = self._calculate_bias_indicators(factor_scores, facet_scores)
       
        return DPQResults(
            dog_id=dog_id,
            assessment_date=datetime.now().isoformat(),
            raw_scores=responses,
            factor_scores=factor_scores,
            facet_scores=facet_scores,
            personality_profile=personality_profile,
            bias_indicators=bias_indicators
        )

    def _generate_personality_profile(self, factor_scores: Dict[str, float],
                                    facet_scores: Dict[str, float]) -> Dict[str, str]:
        """Generate interpretive personality profile"""
        profile = {}
       
        # Factor interpretations
        for factor, score in factor_scores.items():
            if score >= 5.5:
                level = "High"
            elif score >= 4.5:
                level = "Moderate"
            else:
                level = "Low"
            profile[factor] = level
       
        # Overall personality summary
        dominant_traits = []
        if factor_scores["Factor 1 - Fearfulness"] >= 5.0:
            dominant_traits.append("Cautious/Fearful")
        if factor_scores["Factor 2 - Aggression towards People"] >= 5.0:
            dominant_traits.append("Protective/Aggressive")
        if factor_scores["Factor 3 - Activity/Excitability"] >= 5.0:
            dominant_traits.append("Energetic/Excitable")
        if factor_scores["Factor 4 - Responsiveness to Training"] >= 5.0:
            dominant_traits.append("Trainable/Responsive")
        if factor_scores["Factor 5 - Aggression towards Animals"] >= 5.0:
            dominant_traits.append("Animal-Reactive")
       
        if not dominant_traits:
            dominant_traits.append("Balanced")
       
        profile["Dominant_Traits"] = ", ".join(dominant_traits)
       
        return profile

    def _calculate_bias_indicators(self, factor_scores: Dict[str, float],
                                 facet_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate bias indicators for AI translation system"""
       
        bias_indicators = {
            # Communication biases
            "fearfulness_bias": factor_scores["Factor 1 - Fearfulness"] / 7.0,
            "aggression_bias": (factor_scores["Factor 2 - Aggression towards People"] +
                              factor_scores["Factor 5 - Aggression towards Animals"]) / 14.0,
            "excitability_bias": factor_scores["Factor 3 - Activity/Excitability"] / 7.0,
            "trainability_bias": factor_scores["Factor 4 - Responsiveness to Training"] / 7.0,
           
            # Specific behavioral biases
            "social_confidence": (7 - facet_scores["Fear of People"]) / 7.0,
            "dog_sociability": (7 - facet_scores["Fear of Dogs"] + facet_scores["Playfulness"]) / 14.0,
            "environmental_adaptability": (7 - facet_scores["Nonsocial Fear"]) / 7.0,
            "handling_tolerance": (7 - facet_scores["Fear of Handling"]) / 7.0,
           
            # Energy and attention biases
            "attention_seeking": facet_scores["Companionability"] / 7.0,
            "activity_level": (facet_scores["Excitability"] + facet_scores["Active Engagement"]) / 14.0,
            "impulse_control": facet_scores["Controllability"] / 7.0,
           
            # Territorial and protective biases
            "territorial_tendency": facet_scores["General Aggression"] / 7.0,
            "resource_guarding": facet_scores["Situational Aggression"] / 7.0,
            "prey_drive": facet_scores["Prey Drive"] / 7.0
        }
       
        return bias_indicators


class DPQAnalyzer:
    """
    Analyzer class for DPQ results - handles reporting, visualization, and data management
    """
    
    def __init__(self):
        self.factor_descriptions = {
            "Factor 1 - Fearfulness": {
                "description": "Measures anxiety, fear responses, and confidence levels",
                "high": "Dog shows high anxiety, fear of people/situations, low confidence",
                "low": "Dog is confident, calm, and comfortable in various situations"
            },
            "Factor 2 - Aggression towards People": {
                "description": "Measures aggressive tendencies toward humans",
                "high": "Dog shows protective/aggressive behaviors toward people",
                "low": "Dog is friendly and non-aggressive toward people"
            },
            "Factor 3 - Activity/Excitability": {
                "description": "Measures energy levels, playfulness, and engagement",
                "high": "Dog is highly energetic, excitable, and active",
                "low": "Dog is calm, low-energy, and less active"
            },
            "Factor 4 - Responsiveness to Training": {
                "description": "Measures trainability and responsiveness to commands",
                "high": "Dog is highly trainable and responsive to commands",
                "low": "Dog may be stubborn or less responsive to training"
            },
            "Factor 5 - Aggression towards Animals": {
                "description": "Measures aggressive tendencies toward other animals",
                "high": "Dog shows aggressive behaviors toward other animals",
                "low": "Dog is friendly and non-aggressive toward other animals"
            }
        }
        
        self.bias_descriptions = {
            "fearfulness_bias": "Tendency to interpret neutral signals as threatening",
            "aggression_bias": "Likelihood of aggressive response interpretations",
            "excitability_bias": "Tendency toward high-energy interpretations",
            "trainability_bias": "Responsiveness to command-like communications",
            "social_confidence": "Comfort level in social interactions",
            "dog_sociability": "Friendliness toward other dogs",
            "environmental_adaptability": "Comfort with new environments/situations",
            "handling_tolerance": "Acceptance of physical handling/restraint",
            "attention_seeking": "Desire for human interaction and attention",
            "activity_level": "General energy and movement preferences",
            "impulse_control": "Ability to control immediate responses",
            "territorial_tendency": "Protective behavior toward territory/family",
            "resource_guarding": "Protective behavior toward valued items",
            "prey_drive": "Interest in chasing/hunting behaviors"
        }
    
    def generate_report(self, results: DPQResults) -> str:
        """Generate a comprehensive assessment report"""
        
        report = f"""
{'='*80}
DOG PERSONALITY ASSESSMENT REPORT
{'='*80}

Dog ID: {results.dog_id}
Assessment Date: {results.assessment_date}
Total Questions Completed: {len(results.raw_scores)}

{'='*80}
PERSONALITY FACTOR SCORES
{'='*80}

"""
        
        # Factor scores section
        for factor, score in results.factor_scores.items():
            interpretation = results.personality_profile.get(factor, "Unknown")
            description = self.factor_descriptions.get(factor, {})
            
            report += f"{factor}:\n"
            report += f"  Score: {score:.2f}/7.00 ({interpretation})\n"
            report += f"  Description: {description.get('description', 'No description available')}\n"
            
            if interpretation == "High":
                report += f"  Interpretation: {description.get('high', '')}\n"
            elif interpretation == "Low":
                report += f"  Interpretation: {description.get('low', '')}\n"
            else:
                report += f"  Interpretation: Moderate levels of this trait\n"
            report += "\n"
        
        # Personality summary
        report += f"""
{'='*80}
PERSONALITY SUMMARY
{'='*80}

Dominant Traits: {results.personality_profile.get('Dominant_Traits', 'Unknown')}

"""
        
        # Bias indicators section
        report += f"""
{'='*80}
AI TRANSLATION BIAS INDICATORS
{'='*80}

These indicators help calibrate AI translation systems to your dog's personality:

"""
        
        # Group bias indicators by category
        communication_biases = ["fearfulness_bias", "aggression_bias", "excitability_bias", "trainability_bias"]
        social_biases = ["social_confidence", "dog_sociability", "environmental_adaptability", "handling_tolerance"]
        behavioral_biases = ["attention_seeking", "activity_level", "impulse_control"]
        protective_biases = ["territorial_tendency", "resource_guarding", "prey_drive"]
        
        categories = [
            ("Communication Interpretation Biases", communication_biases),
            ("Social Interaction Biases", social_biases),
            ("Behavioral Response Biases", behavioral_biases),
            ("Protective/Territorial Biases", protective_biases)
        ]
        
        for category_name, bias_list in categories:
            report += f"\n{category_name}:\n"
            report += "-" * len(category_name) + "\n"
            
            for bias in bias_list:
                if bias in results.bias_indicators:
                    value = results.bias_indicators[bias]
                    description = self.bias_descriptions.get(bias, "No description available")
                    level = self._interpret_bias_level(value)
                    
                    report += f"  {bias.replace('_', ' ').title()}: {value:.3f} ({level})\n"
                    report += f"    → {description}\n"
        
        # Recommendations section
        report += f"""

{'='*80}
AI TRANSLATION RECOMMENDATIONS
{'='*80}

Based on this personality profile, AI translation systems should:

"""
        
        recommendations = self._generate_recommendations(results)
        for rec in recommendations:
            report += f"• {rec}\n"
        
        report += f"\n{'='*80}\n"
        
        return report
    
    def _interpret_bias_level(self, value: float) -> str:
        """Interpret bias indicator levels"""
        if value >= 0.7:
            return "High"
        elif value >= 0.4:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_recommendations(self, results: DPQResults) -> List[str]:
        """Generate AI translation recommendations based on personality profile"""
        recommendations = []
        
        # Fearfulness recommendations
        if results.bias_indicators.get("fearfulness_bias", 0) > 0.6:
            recommendations.append("Use calm, reassuring tones and avoid sudden or loud vocalizations")
            recommendations.append("Interpret neutral behaviors as potentially anxiety-related")
        
        # Aggression recommendations
        if results.bias_indicators.get("aggression_bias", 0) > 0.5:
            recommendations.append("Be cautious with territorial or protective interpretations")
            recommendations.append("Avoid aggressive or confrontational communication styles")
        
        # Excitability recommendations
        if results.bias_indicators.get("excitability_bias", 0) > 0.6:
            recommendations.append("Expect high-energy responses and enthusiastic communications")
            recommendations.append("May need to moderate excitement levels in translations")
        
        # Training responsiveness
        if results.bias_indicators.get("trainability_bias", 0) > 0.6:
            recommendations.append("Dog likely responds well to clear commands and structure")
        else:
            recommendations.append("May need more patience and alternative communication approaches")
        
        # Social recommendations
        if results.bias_indicators.get("social_confidence", 0) < 0.4:
            recommendations.append("Approach social situations gradually and with extra care")
        
        if results.bias_indicators.get("dog_sociability", 0) < 0.4:
            recommendations.append("Be cautious around other dogs, may prefer human company")
        
        # Activity level recommendations
        if results.bias_indicators.get("activity_level", 0) > 0.6:
            recommendations.append("Expect active, movement-oriented communications")
        else:
            recommendations.append("Dog may prefer calm, low-energy interactions")
        
        return recommendations
    
    def save_results(self, results: DPQResults, filepath: str) -> None:
        """Save DPQ results to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(asdict(results), f, indent=2)
            print(f"Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def load_results(self, filepath: str) -> DPQResults:
        """Load DPQ results from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return DPQResults(**data)
        except Exception as e:
            print(f"Error loading results: {e}")
            return None
    
    def compare_assessments(self, results_list: List[DPQResults]) -> Dict:
        """Compare multiple assessments (e.g., over time)"""
        if len(results_list) < 2:
            return {"error": "Need at least 2 assessments to compare"}
        
        comparison = {
            "assessments": len(results_list),
            "date_range": f"{results_list[0].assessment_date} to {results_list[-1].assessment_date}",
            "factor_changes": {},
            "bias_changes": {}
        }
        
        # Calculate changes in factor scores
        first_assessment = results_list[0]
        last_assessment = results_list[-1]
        
        for factor in first_assessment.factor_scores:
            change = last_assessment.factor_scores[factor] - first_assessment.factor_scores[factor]
            comparison["factor_changes"][factor] = {
                "initial": first_assessment.factor_scores[factor],
                "final": last_assessment.factor_scores[factor],
                "change": change,
                "direction": "increased" if change > 0.2 else "decreased" if change < -0.2 else "stable"
            }
        
        # Calculate changes in bias indicators
        for bias in first_assessment.bias_indicators:
            change = last_assessment.bias_indicators[bias] - first_assessment.bias_indicators[bias]
            comparison["bias_changes"][bias] = {
                "initial": first_assessment.bias_indicators[bias],
                "final": last_assessment.bias_indicators[bias],
                "change": change,
                "direction": "increased" if change > 0.1 else "decreased" if change < -0.1 else "stable"
            }
        
        return comparison


# Create an instance and display the questionnaire
if __name__ == "__main__":
    dpq = DogPersonalityQuestionnaire()
    print("DPQ Implementation Created Successfully!")
    print(f"Total questions: {len(dpq.questions)}")
    print(f"Factors assessed: {len(dpq.scoring_structure)}")

    # Display the questionnaire structure
    print("\n" + "="*60)
    print("QUESTIONNAIRE STRUCTURE:")
    print("="*60)
    for factor, facets in dpq.scoring_structure.items():
        print(f"\n{factor}:")
        for facet, info in facets.items():
            items_str = ", ".join([str(i) for i in info["items"]])
            reverse_str = ", ".join([str(i) for i in info["reverse"]]) if info["reverse"] else "None"
            print(f"  • {facet}: Items {items_str} (Reverse: {reverse_str})")
