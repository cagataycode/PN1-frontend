import asyncio
import json
import os
import uuid
from datetime import datetime, date
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

class TestDPQDatabase:
    """Test DPQ database integration"""
    
    def __init__(self):
        self.test_results = []
        self.test_user_id = str(uuid.uuid4())
        self.test_dog_id = str(uuid.uuid4())
        self.test_assessment_id = str(uuid.uuid4())
        
    async def get_db_connection(self):
        """Get database connection"""
        conn = await asyncpg.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "6543"),
            statement_cache_size=0  # Fix pgbouncer issue
        )
        return conn
    
    def log_test(self, test_name: str, passed: bool, error: str = None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'error': error
        })
        error_msg = f" - {error}" if error else ""
        print(f"  {status}: {test_name}{error_msg}")
    
    def create_test_assessment_data(self):
        """Create test assessment data"""
        from datetime import datetime, date
        
        return {
            'assessment_id': self.test_assessment_id,
            'dog_id': self.test_dog_id,
            'user_id': self.test_user_id,
            'started_at': datetime.now(),  # Changed from string to datetime
            'completed_at': datetime.now(),  # Changed from string to datetime
            'assessment_duration_minutes': 15,
            'device_type': 'desktop',
            'app_version': '1.0.0',
            'dog_info': {
                'name': 'TestDog',
                'breed': 'Golden Retriever',
                'birthday': date(2020, 1, 1)  # Changed from string to date object
            },
            'responses': {str(i): 4 for i in range(1, 46)},  # All moderate responses
            'personality_factors': {
                'fearfulness': {'score': 4.0, 'level': 'Moderate'},
                'aggression_people': {'score': 2.0, 'level': 'Low'},
                'activity_excitability': {'score': 5.0, 'level': 'High'},
                'training_responsiveness': {'score': 6.0, 'level': 'High'},
                'aggression_animals': {'score': 3.0, 'level': 'Moderate'}
            },
            'ai_bias_indicators': {
                'excitability_bias': 0.7,
                'fearfulness_bias': 0.4,
                'trainability_bias': 0.8
            },
            'personality_summary': {
                'dominant_traits': ['Energetic', 'Trainable'],
                'primary_type': 'High-Energy Companion',
                'key_characteristics': ['Very energetic and playful', 'Highly trainable']
            },
            'ai_translator_config': {
                'communication_style': 'energetic_friendly',
                'tone_adjustments': {
                    'base_energy_level': 'high',
                    'excitement_threshold': 0.7
                }
            },
            'recommendations': {
                'training_tips': ['Use positive reinforcement'],
                'exercise_needs': ['High daily exercise'],
                'ai_translator_tips': ['Expect enthusiastic responses']
            },
            'quality_metrics': {
                'reliability_score': 0.94,
                'response_consistency': 'high',
                'extreme_response_bias': False,
                'all_questions_answered': True
            },
            'metadata': {
                'assessment_version': 'DPQ_Short_Form_v1.0',
                'scoring_algorithm': 'Jones_2009_validated'
            }
        }
        
    async def test_database_connection(self):
        """Test database connection"""
        try:
            conn = await self.get_db_connection()
            result = await conn.fetch("SELECT 1 as test")
            await conn.close()
            
            if result and result[0]['test'] == 1:
                self.log_test("Database connection", True)
                return True
            else:
                self.log_test("Database connection", False, "No result returned")
                return False
                
        except Exception as e:
            self.log_test("Database connection", False, str(e))
            return False
    
    async def test_tables_exist(self):
        """Test that DPQ tables exist"""
        try:
            conn = await self.get_db_connection()
            
            # Check dogs table
            dogs_result = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'dogs' AND table_schema = 'public'
            """)
            
            # Check dpq_assessments table
            assessments_result = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'dpq_assessments' AND table_schema = 'public'
            """)
            
            await conn.close()
            
            if dogs_result and assessments_result:
                self.log_test("DPQ tables exist", True)
                return True
            else:
                missing = []
                if not dogs_result:
                    missing.append("dogs")
                if not assessments_result:
                    missing.append("dpq_assessments")
                self.log_test("DPQ tables exist", False, f"Missing tables: {missing}")
                return False
                
        except Exception as e:
            self.log_test("DPQ tables exist", False, str(e))
            return False
    async def create_test_user(self):
        """Create test user for foreign key constraint"""
        try:
            conn = await self.get_db_connection()
            
            # Check if user already exists
            existing_user = await conn.fetchrow("""
                SELECT user_id FROM users WHERE user_id = $1::uuid
            """, self.test_user_id)
            
            if not existing_user:
                await conn.execute("""
                    INSERT INTO users (user_id, email, password)
                    VALUES ($1::uuid, $2, $3)
                """, 
                self.test_user_id,
                f"test_{self.test_user_id}@example.com",
                "test_password_hash"
                )
            
            await conn.close()
            self.log_test("Create test user", True)
            return True
            
        except Exception as e:
            self.log_test("Create test user", False, str(e))
            return False

    async def cleanup_test_data(self):
        """Clean up test data"""
        try:
            conn = await self.get_db_connection()
            
            # Delete in correct order due to foreign keys
            await conn.execute("DELETE FROM dpq_assessments WHERE assessment_id = $1", self.test_assessment_id)
            await conn.execute("DELETE FROM dogs WHERE dog_id = $1", self.test_dog_id)
            await conn.execute("DELETE FROM users WHERE user_id = $1::uuid", self.test_user_id)
            
            await conn.close()
            self.log_test("Cleanup test data", True)
            
        except Exception as e:
            self.log_test("Cleanup test data", False, str(e))

    async def test_insert_dog(self):
        """Test inserting dog data"""
        try:
            conn = await self.get_db_connection()
            test_data = self.create_test_assessment_data()
            dog_info = test_data['dog_info']
            
            await conn.execute("""
                INSERT INTO dogs (dog_id, user_id, name, breed, birthday)
                VALUES ($1, $2::uuid, $3, $4, $5)
            """, 
            self.test_dog_id,
            self.test_user_id,
            dog_info['name'],
            dog_info['breed'],
            dog_info['birthday']
            )
            
            # Verify insertion
            result = await conn.fetchrow("""
                SELECT * FROM dogs WHERE dog_id = $1
            """, self.test_dog_id)
            
            await conn.close()
            
            if result and result['name'] == 'TestDog':
                self.log_test("Insert dog data", True)
                return True
            else:
                self.log_test("Insert dog data", False, "Dog not found after insertion")
                return False
                
        except Exception as e:
            self.log_test("Insert dog data", False, str(e))
            return False
    
    async def test_insert_assessment(self):
        """Test inserting assessment data"""
        try:
            conn = await self.get_db_connection()
            test_data = self.create_test_assessment_data()
            
            await conn.execute("""
                INSERT INTO dpq_assessments (
                    assessment_id, dog_id, user_id, started_at, completed_at,
                    assessment_duration_minutes, device_type, app_version,
                    responses, personality_factors, ai_bias_indicators,
                    personality_summary, ai_translator_config, recommendations,
                    reliability_score, response_consistency, extreme_response_bias,
                    all_questions_answered, assessment_version, scoring_algorithm
                ) VALUES ($1, $2, $3::uuid, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
            """,
            test_data['assessment_id'],
            test_data['dog_id'],
            test_data['user_id'],
            test_data['started_at'],
            test_data['completed_at'],
            test_data['assessment_duration_minutes'],
            test_data['device_type'],
            test_data['app_version'],
            json.dumps(test_data['responses']),
            json.dumps(test_data['personality_factors']),
            json.dumps(test_data['ai_bias_indicators']),
            json.dumps(test_data['personality_summary']),
            json.dumps(test_data['ai_translator_config']),
            json.dumps(test_data['recommendations']),
            test_data['quality_metrics']['reliability_score'],
            test_data['quality_metrics']['response_consistency'],
            test_data['quality_metrics']['extreme_response_bias'],
            test_data['quality_metrics']['all_questions_answered'],
            test_data['metadata']['assessment_version'],
            test_data['metadata']['scoring_algorithm']
            )
            
            # Verify insertion
            result = await conn.fetchrow("""
                SELECT * FROM dpq_assessments WHERE assessment_id = $1
            """, self.test_assessment_id)
            
            await conn.close()
            
            if result and result['assessment_version'] == 'DPQ_Short_Form_v1.0':
                self.log_test("Insert assessment data", True)
                return True
            else:
                self.log_test("Insert assessment data", False, "Assessment not found after insertion")
                return False
                
        except Exception as e:
            self.log_test("Insert assessment data", False, str(e))
            return False
    
    async def test_update_dog_current_assessment(self):
        """Test updating dog's current assessment reference"""
        try:
            conn = await self.get_db_connection()
            
            await conn.execute("""
                UPDATE dogs SET current_dpq_assessment_id = $1 WHERE dog_id = $2
            """, self.test_assessment_id, self.test_dog_id)
            
            # Verify update
            result = await conn.fetchrow("""
                SELECT current_dpq_assessment_id FROM dogs WHERE dog_id = $1
            """, self.test_dog_id)
            
            await conn.close()
            
            if result and str(result['current_dpq_assessment_id']) == self.test_assessment_id:
                self.log_test("Update dog current assessment", True)
                return True
            else:
                self.log_test("Update dog current assessment", False, "Assessment ID not updated")
                return False
                
        except Exception as e:
            self.log_test("Update dog current assessment", False, str(e))
            return False
    
    async def test_retrieve_full_profile(self):
        """Test retrieving complete dog profile with assessment"""
        try:
            conn = await self.get_db_connection()
            
            result = await conn.fetchrow("""
                SELECT d.*, da.* 
                FROM dogs d
                LEFT JOIN dpq_assessments da ON d.current_dpq_assessment_id = da.assessment_id
                WHERE d.dog_id = $1
            """, self.test_dog_id)
            
            await conn.close()
            
            if (result and result['name'] == 'TestDog' and 
                result['assessment_version'] == 'DPQ_Short_Form_v1.0'):
                self.log_test("Retrieve full profile", True)
                return True
            else:
                self.log_test("Retrieve full profile", False, "Profile data incomplete")
                return False
                
        except Exception as e:
            self.log_test("Retrieve full profile", False, str(e))
            return False
    
    async def cleanup_test_data(self):
        """Clean up test data"""
        try:
            conn = await self.get_db_connection()
            
            # Delete in correct order due to foreign keys
            # 1. First clear the foreign key reference
            await conn.execute("UPDATE dogs SET current_dpq_assessment_id = NULL WHERE dog_id = $1", self.test_dog_id)
            
            # 2. Then delete the assessment
            await conn.execute("DELETE FROM dpq_assessments WHERE assessment_id = $1", self.test_assessment_id)
            
            # 3. Then delete the dog
            await conn.execute("DELETE FROM dogs WHERE dog_id = $1", self.test_dog_id)
            
            # 4. Finally delete the user
            await conn.execute("DELETE FROM users WHERE user_id = $1::uuid", self.test_user_id)
            
            await conn.close()
            self.log_test("Cleanup test data", True)
            
        except Exception as e:
            self.log_test("Cleanup test data", False, str(e))
        
    async def run_all_tests(self):
        """Run all database tests"""
        print("🔍 Testing DPQ Database Integration...")
        print("=" * 50)
        
        # Test database connection first
        if not await self.test_database_connection():
            print("\n❌ Database connection failed - skipping other tests")
            return False
        
        # Test table existence
        if not await self.test_tables_exist():
            print("\n❌ Required tables missing - skipping data tests")
            return False
        
        # Create test user first
        if not await self.create_test_user():
            print("\n❌ Failed to create test user - skipping data tests")
            return False
        
        # Run data tests
        tests = [
            self.test_insert_dog,
            self.test_insert_assessment,
            self.test_update_dog_current_assessment,
            self.test_retrieve_full_profile
        ]
        
        for test in tests:
            await test()
        
        # Cleanup
        await self.cleanup_test_data()
        
        # Calculate results
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 Database integration is working well!")
        else:
            print("⚠️  Some database tests failed - check the errors above")
        
        return success_rate >= 80

async def main():
    """Run the database tests"""
    tester = TestDPQDatabase()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
