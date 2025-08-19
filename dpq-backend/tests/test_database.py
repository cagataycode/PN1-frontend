# Test script for database connection
import asyncio
import os
import json
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

async def test_database_connection():
    """Test database connection and basic operations"""
    
    print("🗄️ Testing Database Connection...")
    print("=" * 50)
    
    # Check if DATABASE_URL exists
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables!")
        print("Please add it to your .env file")
        return False
    
    print(f"✅ DATABASE_URL found: {database_url[:30]}...")
    
    # Test connection
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    
    # Test basic query
    try:
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Basic query test successful: {result}")
    except Exception as e:
        print(f"❌ Basic query failed: {str(e)}")
        await conn.close()
        return False
    
    # Test table existence
    tables_to_check = ['users', 'videos', 'frames', 'subscriptions']
    print("\n📋 Checking table existence:")
    
    for table in tables_to_check:
        try:
            result = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if result:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
        except Exception as e:
            print(f"❌ Error checking table '{table}': {str(e)}")
    
    # Test column existence for new JSON columns (updated for Fontaine model)
    print("\n🔍 Checking new columns:")

    json_columns = [
        ('videos', 'translation_results'),
        ('videos', 'video_emotion_classification'),
        ('frames', 'emotion_classification'),
        ('frames', 'original_image_base64'),
        ('videos', 'original_video_base64')  # Add this line
    ]

    
    for table, column in json_columns:
        try:
            result = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = $1 AND column_name = $2
                )
            """, table, column)
            
            if result:
                print(f"✅ Column '{table}.{column}' exists")
            else:
                print(f"❌ Column '{table}.{column}' missing")
        except Exception as e:
            print(f"❌ Error checking column '{table}.{column}': {str(e)}")
    
    # Test JSON operations with new Fontaine model structure
    print("\n🧪 Testing JSON operations:")
    
    try:
        # Test JSON insertion and retrieval with new emotion classification format
        test_video_emotion = {
            "primary_emotion": "Joy",
            "secondary_emotion": "Interest"
        }

        test_translation_results = {
            "body_language_analysis": "Test analysis",
            "behavior_description": "Test behavior", 
            "emotional_state": "Test emotion",
            "behavior_reason": "Test reason",
            "dog_quote": "Woof! I'm so happy right now!"  # Add this line
        }

        test_frame_emotion = {
            "primary_emotion": "Joy", 
            "secondary_emotion": None
        }
        
        # Create a test record (if videos table exists)
        import uuid
        test_video_id = str(uuid.uuid4())
        test_video_base64 = "UklGRjIAAABXRUJQVlA4ICYAAACyAgCdASoBAAEALmk0mk0iIiIiIgBoSygABc6zbAAA/v56QAAAAA=="  # Tiny test video
        await conn.execute("""
            INSERT INTO videos (video_id, user_id, video_path, video_emotion_classification, original_video_base64, translation_results) 
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (video_id) DO UPDATE SET video_emotion_classification = $4, original_video_base64 = $5, translation_results = $6
        """, test_video_id, None, "/test/path", json.dumps(test_video_emotion), test_video_base64, json.dumps(test_translation_results))

        # Test frame insertion with image data
        test_frame_id = str(uuid.uuid4())
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="  # Tiny test image
        await conn.execute("""
            INSERT INTO frames (frame_id, video_id, frame_path, timestamp, emotion, emotion_classification, original_image_base64)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (frame_id) DO UPDATE SET emotion_classification = $6, original_image_base64 = $7
        """, test_frame_id, test_video_id, "/test/frame.jpg", 1.5, "Joy", json.dumps(test_frame_emotion), test_image_base64)

        
        # Retrieve and verify video emotion
        result = await conn.fetchval(
            "SELECT video_emotion_classification FROM videos WHERE video_id = $1",
            test_video_id
        )
        
        if result:
            parsed_json = json.loads(result)
            if parsed_json == test_video_emotion:
                print("✅ Video emotion classification storage successful")
            else:
                print(f"❌ Video emotion JSON mismatch: expected {test_video_emotion}, got {parsed_json}")
        else:
            print("❌ Video emotion retrieval failed")
        
        # Retrieve and verify frame emotion
        result = await conn.fetchval(
            "SELECT emotion_classification FROM frames WHERE frame_id = $1",
            test_frame_id
        )
        
        if result:
            parsed_json = json.loads(result)
            if parsed_json == test_frame_emotion:
                print("✅ Frame emotion classification storage successful")
            else:
                print(f"❌ Frame emotion JSON mismatch: expected {test_frame_emotion}, got {parsed_json}")
        else:
            print("❌ Frame emotion retrieval failed")

        # Test video base64 storage and retrieval
        video_base64_result = await conn.fetchval(
            "SELECT original_video_base64 FROM videos WHERE video_id = $1",
            test_video_id
        )

        if video_base64_result == test_video_base64:
            print("✅ Video base64 storage successful")
        else:
            print("❌ Video base64 storage failed")


        # Test image storage and retrieval
        image_result = await conn.fetchval(
            "SELECT original_image_base64 FROM frames WHERE frame_id = $1",
            test_frame_id
        )

        if image_result == test_image_base64:
            print("✅ Image base64 storage successful")
        else:
            print("❌ Image base64 storage failed")        
            
        # Clean up test data
        await conn.execute("DELETE FROM frames WHERE frame_id = $1", test_frame_id)
        await conn.execute("DELETE FROM videos WHERE video_id = $1", test_video_id)
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ JSON operations test failed: {str(e)}")


    # Test database version
    try:
        version = await conn.fetchval("SELECT version()")
        print(f"\n📊 Database version: {version.split(',')[0]}")
    except Exception as e:
        print(f"❌ Could not get database version: {str(e)}")
    
    await conn.close()
    print("✅ Database connection closed")
    
    return True

async def main():
    """Main test function"""
    success = await test_database_connection()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Database connection tests completed!")
    else:
        print("\n" + "=" * 50)
        print("❌ Database tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
