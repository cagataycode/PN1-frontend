# jobs/emotion_mapper.py
"""
Emotion dimension mapper using 4-dimensional framework
Maps emotions to Positive/Negative, Extrinsic/Intrinsic, Stimulated/Chill, Unpredictable/Predictable
"""

# Emotion coefficient mapping table
EMOTION_COEFFICIENTS = {
    "Contentment": {
        "positive_negative": 0.5,
        "extrinsic_intrinsic": -0.7,
        "stimulated_chill": -0.9,
        "unpredictable_predictable": -1.0
    },
    "Despair": {
        "positive_negative": -0.9,
        "extrinsic_intrinsic": -0.8,
        "stimulated_chill": -1.0,
        "unpredictable_predictable": -1.0
    },
    "Love": {
        "positive_negative": 0.9,
        "extrinsic_intrinsic": -0.7,
        "stimulated_chill": -0.2,
        "unpredictable_predictable": -1.0
    },
    "Hate": {
        "positive_negative": -0.9,
        "extrinsic_intrinsic": -0.5,
        "stimulated_chill": 0.8,
        "unpredictable_predictable": -0.9
    },
    "Pride": {
        "positive_negative": 0.4,
        "extrinsic_intrinsic": -0.9,
        "stimulated_chill": 0.3,
        "unpredictable_predictable": -0.9
    },
    "Compassion": {
        "positive_negative": 0.3,
        "extrinsic_intrinsic": 0.3,
        "stimulated_chill": -0.6,
        "unpredictable_predictable": -0.8
    },
    "Contempt": {
        "positive_negative": -0.4,
        "extrinsic_intrinsic": -0.6,
        "stimulated_chill": -0.1,
        "unpredictable_predictable": -0.8
    },
    "Sadness": {
        "positive_negative": -0.8,
        "extrinsic_intrinsic": -0.5,
        "stimulated_chill": -0.8,
        "unpredictable_predictable": -0.8
    },
    "Guilt": {
        "positive_negative": -0.5,
        "extrinsic_intrinsic": -1.0,
        "stimulated_chill": 0.1,
        "unpredictable_predictable": -0.7
    },
    "Pleasure": {
        "positive_negative": 0.6,
        "extrinsic_intrinsic": 0.2,
        "stimulated_chill": 0.4,
        "unpredictable_predictable": -0.7
    },
    "Hurt": {
        "positive_negative": -0.2,
        "extrinsic_intrinsic": 0.9,
        "stimulated_chill": -0.3,
        "unpredictable_predictable": -0.6
    },
    "Happiness": {
        "positive_negative": 0.7,
        "extrinsic_intrinsic": -0.5,
        "stimulated_chill": 0.2,
        "unpredictable_predictable": -0.5
    },
    "Disappointment": {
        "positive_negative": -0.6,
        "extrinsic_intrinsic": 0.7,
        "stimulated_chill": -0.5,
        "unpredictable_predictable": 0.7
    },
    "Anxiety": {
        "positive_negative": -0.5,
        "extrinsic_intrinsic": -0.2,
        "stimulated_chill": 0.8,
        "unpredictable_predictable": 0.4
    },
    "Interest": {
        "positive_negative": 0.3,
        "extrinsic_intrinsic": 0.7,
        "stimulated_chill": 0.4,
        "unpredictable_predictable": 0.2
    },
    "Joy": {
        "positive_negative": 0.8,
        "extrinsic_intrinsic": -0.4,
        "stimulated_chill": 0.9,
        "unpredictable_predictable": 0.2
    },
    "Anger": {
        "positive_negative": -0.7,
        "extrinsic_intrinsic": 0.6,
        "stimulated_chill": 1.0,
        "unpredictable_predictable": 0.4
    },
    "Jealousy": {
        "positive_negative": -0.6,
        "extrinsic_intrinsic": 0.4,
        "stimulated_chill": 0.2,
        "unpredictable_predictable": 0.4
    },
    "Irritation": {
        "positive_negative": -0.1,
        "extrinsic_intrinsic": 0.6,
        "stimulated_chill": 0.3,
        "unpredictable_predictable": 0.5
    },
    "Stress": {
        "positive_negative": -0.3,
        "extrinsic_intrinsic": -0.1,
        "stimulated_chill": 0.7,
        "unpredictable_predictable": 0.3
    },
    "Disgust": {
        "positive_negative": -0.4,
        "extrinsic_intrinsic": 0.7,
        "stimulated_chill": 0.5,
        "unpredictable_predictable": 0.7
    },
    "Shame": {
        "positive_negative": -0.6,
        "extrinsic_intrinsic": -0.8,
        "stimulated_chill": -0.3,
        "unpredictable_predictable": 0.8
    },
    "Fear": {
        "positive_negative": -0.6,
        "extrinsic_intrinsic": 0.6,
        "stimulated_chill": 0.9,
        "unpredictable_predictable": 0.9
    },
    "Surprise": {
        "positive_negative": 0.0,
        "extrinsic_intrinsic": 1.0,
        "stimulated_chill": 1.0,
        "unpredictable_predictable": 1.0
    }
}

def calculate_weighted_dimensions(primary_emotion, secondary_emotion=None, primary_weight=0.7, secondary_weight=0.3):
    """
    Calculate 4D emotion dimensions using weighted average of primary and secondary emotions
    
    Args:
        primary_emotion (str): Primary emotion name
        secondary_emotion (str or None): Secondary emotion name
        primary_weight (float): Weight for primary emotion (default 0.7)
        secondary_weight (float): Weight for secondary emotion (default 0.3)
    
    Returns:
        dict: 4D emotion dimensions
    """
    if primary_emotion not in EMOTION_COEFFICIENTS:
        raise ValueError(f"Unknown primary emotion: {primary_emotion}")
    
    primary_coeffs = EMOTION_COEFFICIENTS[primary_emotion]
    
    # If no secondary emotion, use only primary
    if not secondary_emotion:
        return primary_coeffs.copy()
    
    if secondary_emotion not in EMOTION_COEFFICIENTS:
        raise ValueError(f"Unknown secondary emotion: {secondary_emotion}")
    
    secondary_coeffs = EMOTION_COEFFICIENTS[secondary_emotion]
    
    # Calculate weighted average
    weighted_dimensions = {}
    for dimension in primary_coeffs.keys():
        weighted_value = (
            primary_coeffs[dimension] * primary_weight + 
            secondary_coeffs[dimension] * secondary_weight
        )
        # Round to 2 decimal places
        weighted_dimensions[dimension] = round(weighted_value, 2)
    
    return weighted_dimensions

def add_emotion_dimensions(analysis_result):
    """
    Add emotion dimensions to the analysis result
    
    Args:
        analysis_result (dict): Claude analysis result
    
    Returns:
        dict: Analysis result with added emotion dimensions
    """
    try:
        # Get video emotion classification
        video_emotion = analysis_result.get("video_emotion_classification", {})
        primary = video_emotion.get("primary_emotion")
        secondary = video_emotion.get("secondary_emotion")
        
        if primary:
            # Calculate emotion dimensions
            dimensions = calculate_weighted_dimensions(primary, secondary)
            
            # Add to video emotion classification
            analysis_result["video_emotion_classification"]["emotion_dimensions"] = dimensions
        
        return analysis_result
        
    except Exception as e:
        print(f"Error adding emotion dimensions: {str(e)}")
        # Return original result if mapping fails
        return analysis_result

# Test function
if __name__ == "__main__":
    # Test the mapping
    test_result = calculate_weighted_dimensions("Joy", "Interest")
    print("Joy + Interest dimensions:", test_result)
    
    test_result2 = calculate_weighted_dimensions("Fear", None)
    print("Fear only dimensions:", test_result2)