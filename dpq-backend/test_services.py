#!/usr/bin/env python3
"""
Test script for the DPQ Backend service layer

This script tests the basic functionality of the service classes to ensure
they can be imported and initialized correctly.
"""

import sys
import os
import asyncio
import logging

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_service_imports():
    """Test that all services can be imported correctly"""
    try:
        logger.info("Testing service imports...")
        
        from app.services import DPQService, ClaudeService, VideoService, ServiceManager
        
        logger.info("✅ All service classes imported successfully")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during import: {e}")
        return False


async def test_service_initialization():
    """Test that services can be initialized"""
    try:
        logger.info("Testing service initialization...")
        
        from app.services import DPQService, ClaudeService, VideoService
        
        # Test DPQ Service
        dpq_service = DPQService()
        logger.info("✅ DPQ Service initialized")
        
        # Test Claude Service (may fail if no API key)
        try:
            claude_service = ClaudeService()
            logger.info("✅ Claude Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Claude Service initialization failed (expected if no API key): {e}")
        
        # Test Video Service
        try:
            video_service = VideoService()
            logger.info("✅ Video Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Video Service initialization failed (expected if no FFmpeg): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization error: {e}")
        return False


async def test_service_manager():
    """Test the service manager"""
    try:
        logger.info("Testing Service Manager...")
        
        from app.services import ServiceManager
        
        # Initialize service manager
        service_manager = ServiceManager()
        logger.info("✅ Service Manager initialized")
        
        # Test service listing
        services = service_manager.list_services()
        logger.info(f"✅ Available services: {services}")
        
        # Test health check
        health = await service_manager.get_service_health()
        logger.info(f"✅ Service health: {health['overall_status']}")
        
        # Test capabilities
        capabilities = await service_manager.get_service_capabilities()
        logger.info(f"✅ Service capabilities retrieved for {len(capabilities)} services")
        
        # Cleanup
        await service_manager.shutdown()
        logger.info("✅ Service Manager shutdown completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service Manager test error: {e}")
        return False


async def test_model_imports():
    """Test that data models can be imported correctly"""
    try:
        logger.info("Testing model imports...")
        
        from app.models import (
            AssessmentRequest, AssessmentResponse, DogInfo,
            APIResponse, ErrorResponse, HealthCheckResponse
        )
        
        logger.info("✅ All model classes imported successfully")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Model import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during model import: {e}")
        return False


async def test_basic_functionality():
    """Test basic service functionality"""
    try:
        logger.info("Testing basic service functionality...")
        
        from app.services import DPQService
        from app.models import DogInfo, AssessmentRequest
        
        # Create a sample dog info
        dog_info = DogInfo(
            name="Test Dog",
            breed="Golden Retriever",
            age="3 years"
        )
        
        # Create sample assessment data
        assessment_data = {
            "dog_info": dog_info.dict(),
            "responses": {
                1: 3, 2: 2, 3: 4, 4: 3, 5: 5,
                6: 2, 7: 1, 8: 4, 9: 3, 10: 2
            }
        }
        
        # Test DPQ service
        dpq_service = DPQService()
        
        # Test personality factors endpoint
        factors = await dpq_service.get_personality_factors()
        logger.info(f"✅ Personality factors retrieved: {len(factors['factors'])} factors")
        
        # Test assessment summary endpoint
        summary = await dpq_service.get_assessment_summary("test_123")
        logger.info(f"✅ Assessment summary retrieved: {summary['status']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic functionality test error: {e}")
        return False


async def main():
    """Main test function"""
    logger.info("🚀 Starting DPQ Backend Service Layer Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Service Imports", test_service_imports),
        ("Model Imports", test_model_imports),
        ("Service Initialization", test_service_initialization),
        ("Service Manager", test_service_manager),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Service layer is working correctly.")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
