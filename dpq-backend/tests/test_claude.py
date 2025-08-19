# Claude API Test Script
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_connection():
    """Test basic connection to Claude API"""
    try:
        # Initialize client
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Test basic message
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, Claude! Please respond with 'Connection successful' if you can read this."}
            ]
        )
        
        print("✅ Claude API Connection Successful!")
        print(f"Response: {message.content[0].text}")
        return True
        
    except Exception as e:
        print("❌ Claude API Connection Failed!")
        print(f"Error: {str(e)}")
        return False

def test_claude_vision():
    """Test Claude's vision capabilities with a simple image"""
    try:
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create a simple test image (you can replace this with an actual image path)
        print("Testing vision capabilities...")
        print("Note: You'll need to provide an actual image file for full vision testing")
        
        # For now, just test text-based emotion analysis
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {
                    "role": "user", 
                    "content": "Can you analyze emotions? Please return a JSON object with emotion scores from 0-1 for these emotions: Happy, Sad, Angry, Surprised, Neutral. Make it a test example."
                }
            ]
        )
        
        print("✅ Claude Vision/Analysis Test Successful!")
        print(f"Response: {message.content[0].text}")
        return True
        
    except Exception as e:
        print("❌ Claude Vision Test Failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Claude API Connection...")
    print("=" * 50)
    
    # Check if API key exists
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables!")
        print("Please add it to your .env file")
        exit(1)
    
    print(f"API Key found: {api_key[:10]}..." if api_key else "No API key")
    print()
    
    # Test basic connection
    if test_claude_connection():
        print()
        # Test vision capabilities
        test_claude_vision()
    
    print()
    print("=" * 50)
    print("Testing complete!")