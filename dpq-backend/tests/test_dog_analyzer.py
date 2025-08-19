# Test script for dog behavior analyzer
import sys
import os

# Add the project root to Python path FIRST
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# NOW import everything else
import asyncio
import json
from dotenv import load_dotenv
import anthropic
from jobs.dog_behavior_analyzer import analyze_frames_with_claude

# Load environment variables
load_dotenv()

async def test_dog_behavior_analyzer():
    """Test the dog behavior analyzer with sample frames"""
    
    print("🐕 Testing Dog Behavior Analyzer...")
    print("=" * 50)
    
    # Check if API key exists
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables!")
        print("Please add it to your .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize Claude client
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Claude client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Claude client: {str(e)}")
        return False
    
    # Check if we have test frames
    test_frames_dir = "tests/test_frames"
    if not os.path.exists(test_frames_dir):
        print(f"❌ Test frames directory '{test_frames_dir}' not found!")
        print("Please create some test frames first by running:")
        print("python jobs/extract_diff_frames.py uploads/[upload_id]/video.mp4 test_frames --ffmpeg-path /workspace/PN1.pwa/bin/ffmpeg")
        return False
    
    # Check if there are any frame files
    frame_files = [f for f in os.listdir(test_frames_dir) if f.endswith('.jpg')]
    if not frame_files:
        print(f"❌ No .jpg files found in '{test_frames_dir}'!")
        print("Please extract some frames first")
        return False
    
    print(f"✅ Found {len(frame_files)} test frames")
    print(f"Frame files: {frame_files[:3]}{'...' if len(frame_files) > 3 else ''}")
    
    # Test the analyzer
    try:
        print("🔍 Starting dog behavior analysis...")
        result = await analyze_frames_with_claude(test_frames_dir, client)
        
        if "error" in result:
            print(f"❌ Analysis failed: {result['error']}")
            if "raw_response" in result:
                print(f"Raw response: {result['raw_response'][:200]}...")
            return False
        
        print("✅ Analysis completed successfully!")
        
        # Display results summary
        if "translation_results" in result:
            print("📊 Analysis Summary:")
            print(f"Body Language: {result['translation_results']['body_language_analysis'][:100]}...")
            print(f"Behavior: {result['translation_results']['behavior_description'][:100]}...")
            print(f"Emotional State: {result['translation_results']['emotional_state'][:100]}...")
            print(f"🐕 Dog Quote: \"{result['translation_results']['dog_quote']}\"")
        
        if "video_emotion_classification" in result:
            print(f"🎯 Overall Emotion Classification:")
            print(f"Primary: {result['video_emotion_classification']['primary_emotion']}")
            secondary = result['video_emotion_classification']['secondary_emotion']
            print(f"Secondary: {secondary if secondary else 'None'}")
            
            # Add emotion dimensions display
            if "emotion_dimensions" in result['video_emotion_classification']:
                dims = result['video_emotion_classification']['emotion_dimensions']
                print(f"📊 Emotion Dimensions:")
                print(f"  Positive/Negative: {dims['positive_negative']}")
                print(f"  Extrinsic/Intrinsic: {dims['extrinsic_intrinsic']}")
                print(f"  Stimulated/Chill: {dims['stimulated_chill']}")
                print(f"  Unpredictable/Predictable: {dims['unpredictable_predictable']}")

        if "frame_data" in result and len(result["frame_data"]) > 0:
            print(f"📋 Frame Analysis:")
            for i, frame in enumerate(result["frame_data"][:3], 1):  # Show first 3 frames
                primary = frame['emotion_classification']['primary_emotion']
                secondary = frame['emotion_classification']['secondary_emotion']
                secondary_text = f" + {secondary}" if secondary else ""
                print(f"Frame {i} ({frame['timestamp']}s): {primary}{secondary_text}")
            if len(result["frame_data"]) > 3:
                print(f"... and {len(result['frame_data']) - 3} more frames")


            
        # Display full analysis for inspection (since we're not saving to file anymore)
        print("\n📄 Full Analysis Results:")
        print("=" * 30)
        import json
        print(json.dumps(result, indent=2))
                
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed with exception: {str(e)}")
        return False

async def main():
    """Main test function"""
    success = await test_dog_behavior_analyzer()
    
    if success:
        print("" + "=" * 50)
        print("🎉 All tests passed! Dog behavior analyzer is working correctly.")
    else:
        print("" + "=" * 50)
        print("❌ Tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())