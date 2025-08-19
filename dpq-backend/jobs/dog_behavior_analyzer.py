import anthropic
import base64
import json
import os
from sanic.log import logger
from jobs.emotion_mapper import add_emotion_dimensions

async def analyze_frames_with_claude(frames_dir: str, client: anthropic.Anthropic) -> dict:
    """Analyze extracted dog frames using Claude's vision capabilities with prompt caching"""
    
    # Get all frame files and sort by timestamp
    frame_files = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
    frame_files.sort(key=lambda x: float(x.replace('frame_', '').replace('.jpg', '')))
    
    if not frame_files:
        return {"error": "No frames found for analysis"}
    
    logger.info(f"Found {len(frame_files)} frames to analyze with cached prompt")
    
    # Prepare images for Claude
    base64_images = []
    
    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        
        with open(frame_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode()
            base64_images.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }
            })
    
    # Cached system prompt
    cached_system_prompt = """You are an expert canine behaviorist and animal psychologist. Analyze the provided video frames of a dog and provide a comprehensive behavioral assessment.

Analysis Requirements:

Body Language Analysis: Examine posture, tail position, ear position, facial expressions, muscle tension, movement patterns, and overall body positioning. Note any subtle behavioral cues.

Behavior Description: Clearly describe what specific actions the dog is performing. Be precise about movements, interactions with environment/objects/people, and behavioral sequences.

Emotional State Assessment: Determine the dog's emotional condition based on observable behavioral indicators. Consider stress signals, comfort levels, arousal states, and overall well-being.

Behavioral Reasoning: Explain the likely motivations, instincts, or triggers behind the observed behavior. Consider evolutionary, physiological, and environmental factors.

Dog Quote: Based on the dog's behavior, body language, and emotional state, provide one sentence that captures what the dog would say if it could speak. This should reflect the dog's perspective, emotions, and intentions in that moment.

Emotion Classification Guidelines:

Select the most appropriate emotions from the following 24-emotion list:

EMOTIONS: Contentment, Despair, Love, Hate, Pride, Compassion, Contempt, Sadness, Guilt, Pleasure, Hurt, Happiness, Disappointment, Anxiety, Interest, Joy, Anger, Jealousy, Irritation, Stress, Disgust, Shame, Fear, Surprise

For each frame and the overall video, identify the primary (dominant) emotion and secondary (supporting) emotion that best represent the dog's emotional state. If only one emotion is clearly present, set secondary_emotion to null.

CRITICAL: You must return your analysis in EXACTLY this JSON format:

{

 "translation_results": {

 "body_language_analysis": "[Your detailed body language analysis here]",

 "behavior_description": "[Your behavior description here]",

 "emotional_state": "[Your emotional state assessment here]",

 "behavior_reason": "[Your behavioral reasoning here]",

 "dog_quote": "[One sentence representing what the dog would say if it could speak]"

 },

 "video_emotion_classification": {

 "primary_emotion": "[one of the 24 emotions]",

 "secondary_emotion": "[one of the 24 emotions]"

 },

 "frame_data": [

 {

 "timestamp": [float in seconds],

 "emotion_classification": {

 "primary_emotion": "[one of the 24 emotions]",

 "secondary_emotion": "[one of the 24 emotions]"

 }

 }

 ]

}

IMPORTANT: 
- Use ONLY the 24 emotions listed above
- Primary emotion is the most dominant emotion observed
- Secondary emotion is the supporting/additional emotion (can be null if only one clear emotion)
- Return ONLY valid JSON - no additional text before or after
- Use exact field names as shown
- Include all required fields
- DO NOT wrap the response in markdown code blocks or backticks - return raw JSON only"""

    try:
        logger.info("Sending frames to Claude for analysis with cached prompt...")
        
        # Send to Claude with cached system prompt
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=[
                {
                    "type": "text",
                    "text": cached_system_prompt,
                    "cache_control": {"type": "ephemeral"}  # Cache this prompt
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": base64_images
                }
            ]
        )
        
        # Log cache usage if available
        if hasattr(message, 'usage'):
            logger.info(f"Token usage: {message.usage}")
        
        # Parse response
        response_text = message.content[0].text.strip()
        
        # Remove markdown if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        logger.info("Received response from Claude, parsing JSON...")
        
        analysis_result = json.loads(response_text)
        logger.info("Successfully parsed Claude response")
        analysis_result = add_emotion_dimensions(analysis_result)
        
        return analysis_result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        return {"error": f"Failed to parse JSON response: {str(e)}", "raw_response": response_text}
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
        return {"error": f"Claude API error: {str(e)}"}
