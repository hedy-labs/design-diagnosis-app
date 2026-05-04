#!/usr/bin/env python3
"""
Cloudflare R2 Health Check - Verify connectivity & bucket access
Tests the cloud storage configuration before activating pre-signed URLs
"""

import sys
import os
import logging

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    # Fallback: manually load .env
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("🔍 CLOUDFLARE R2 HEALTH CHECK")
    logger.info("=" * 70)
    
    # Load cloud storage config
    try:
        from cloud_storage import CloudStorageConfig, CloudStorageManager
        logger.info("✅ Cloud storage modules loaded")
    except ImportError as e:
        logger.error(f"❌ Failed to import cloud_storage: {e}")
        return False
    
    # Initialize config
    config = CloudStorageConfig()
    logger.info(f"\n📋 Configuration:")
    logger.info(f"   Provider: {config.provider}")
    logger.info(f"   Bucket: {config.bucket_name}")
    logger.info(f"   Endpoint: {config.endpoint_url}")
    logger.info(f"   Configured: {config.is_configured}")
    
    if not config.is_configured:
        logger.error("❌ Cloud storage not configured (missing credentials)")
        return False
    
    # Initialize manager
    try:
        logger.info("\n🔗 Initializing cloud manager...")
        manager = CloudStorageManager(config)
        logger.info("✅ Cloud manager initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize cloud manager: {e}")
        return False
    
    # Health check
    try:
        logger.info("\n🏥 Running health check...")
        is_healthy = manager.is_healthy()
        
        if is_healthy:
            logger.info("✅ HEALTH CHECK PASSED - Bucket accessible")
            logger.info(f"✅ R2 bucket '{config.bucket_name}' is online")
        else:
            logger.error("❌ HEALTH CHECK FAILED - Cannot access bucket")
            return False
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False
    
    # Test pre-signed URL generation
    try:
        logger.info("\n🔐 Testing pre-signed URL generation...")
        presigned = manager.generate_presigned_upload_url(
            submission_id=999,
            filename="test.jpg",
            content_type="image/jpeg"
        )
        
        if presigned:
            logger.info("✅ Pre-signed URL generated successfully")
            logger.info(f"   Upload URL (shortened): {presigned['upload_url'][:60]}...")
            logger.info(f"   Public URL (shortened): {presigned['public_url'][:60]}...")
            logger.info(f"   Expires in: {presigned['expires_in']} seconds")
        else:
            logger.error("❌ Failed to generate pre-signed URL")
            return False
    except Exception as e:
        logger.error(f"❌ Pre-signed URL test failed: {e}")
        return False
    
    # Success!
    logger.info("\n" + "=" * 70)
    logger.info("🟢 ALL CHECKS PASSED - R2 CLOUD STORAGE ACTIVE")
    logger.info("=" * 70)
    logger.info("RAM Shield: ACTIVE ✅")
    logger.info("Server images: Will bypass local storage")
    logger.info("Pre-signed URLs: Ready for browser uploads")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
