"""
Cloud Storage Integration for Image Uploads
Handles AWS S3 / Cloudflare R2 pre-signed URLs for direct browser uploads

Eliminates server-side file storage, reduces RAM/disk pressure on Droplet
"""

import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import hashlib

logger = logging.getLogger(__name__)

# ============================================================================
# CLOUD STORAGE CONFIGURATION
# ============================================================================

class CloudStorageConfig:
    """Unified cloud storage configuration (S3 / R2 compatible)"""
    
    def __init__(self):
        # Cloud Provider Selection: AWS S3 or Cloudflare R2
        self.provider = os.getenv('CLOUD_STORAGE_PROVIDER', 'r2')  # 'r2' or 's3'
        
        # Required Credentials
        self.access_key = os.getenv('CLOUD_STORAGE_ACCESS_KEY', '')
        self.secret_key = os.getenv('CLOUD_STORAGE_SECRET_KEY', '')
        self.bucket_name = os.getenv('CLOUD_STORAGE_BUCKET_NAME', '')
        
        # Provider-Specific Endpoints
        self.endpoint_url = os.getenv('CLOUD_STORAGE_ENDPOINT_URL', '')
        self.public_url_base = os.getenv('CLOUD_STORAGE_PUBLIC_URL_BASE', '')
        
        # Region (AWS S3 only)
        self.region = os.getenv('CLOUD_STORAGE_REGION', 'us-east-1')
        
        # Pre-signed URL expiration (seconds)
        self.presigned_url_ttl = int(os.getenv('CLOUD_STORAGE_PRESIGNED_TTL', '3600'))  # 1 hour default
        
        # Upload path prefix
        self.upload_prefix = os.getenv('CLOUD_STORAGE_UPLOAD_PREFIX', 'design-diagnosis/uploads')
        
        # Validation
        self.is_configured = bool(self.access_key and self.secret_key and self.bucket_name)
    
    def __repr__(self):
        return f"CloudStorageConfig(provider={self.provider}, bucket={self.bucket_name}, configured={self.is_configured})"


# ============================================================================
# PRE-SIGNED URL GENERATION
# ============================================================================

class CloudStorageManager:
    """
    Generates pre-signed URLs for direct browser uploads to cloud buckets
    
    Security:
    - URLs expire after 1 hour (configurable)
    - Each upload gets unique key (UUID + timestamp)
    - Restricted to specific bucket path
    - No server-side file storage required
    """
    
    def __init__(self, config: Optional[CloudStorageConfig] = None):
        self.config = config or CloudStorageConfig()
        self.client = None
        
        if self.config.is_configured:
            self._initialize_client()
        else:
            logger.warning("⚠️  Cloud storage not configured. Using local fallback.")
    
    def _initialize_client(self):
        """Initialize S3/R2 client"""
        try:
            if self.config.provider.lower() == 'r2':
                # Cloudflare R2 (S3-compatible)
                import boto3
                self.client = boto3.client(
                    's3',
                    endpoint_url=self.config.endpoint_url,
                    aws_access_key_id=self.config.access_key,
                    aws_secret_access_key=self.config.secret_key,
                    region_name='auto'  # R2 uses 'auto' region
                )
                logger.info(f"✅ Cloudflare R2 client initialized: {self.config.endpoint_url}")
            
            elif self.config.provider.lower() == 's3':
                # AWS S3
                import boto3
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=self.config.access_key,
                    aws_secret_access_key=self.config.secret_key,
                    region_name=self.config.region
                )
                logger.info(f"✅ AWS S3 client initialized: {self.config.region}")
            
            else:
                logger.error(f"❌ Unknown cloud provider: {self.config.provider}")
                self.client = None
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize cloud storage client: {e}")
            self.client = None
    
    def generate_presigned_upload_url(
        self,
        submission_id: int,
        filename: str,
        content_type: str = 'image/jpeg'
    ) -> Dict[str, Any]:
        """
        Generate a pre-signed URL for direct browser upload to cloud bucket
        
        Args:
            submission_id: Database submission ID
            filename: Original filename from user
            content_type: MIME type (image/jpeg, image/png, etc.)
        
        Returns:
            {
                'upload_url': 'https://...',  # Pre-signed URL for browser upload
                'public_url': 'https://...',  # Public URL after upload completes
                'upload_key': 'design-diagnosis/uploads/submission_123/abc-def-456.jpg',
                'expires_in': 3600,           # Seconds until URL expires
                'form_data': {...}            # Additional fields for multipart/form-data (if needed)
            }
        """
        
        if not self.client:
            logger.warning("⚠️  Cloud storage not available, returning None")
            return None
        
        try:
            # Generate unique key
            unique_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1]
            upload_key = f"{self.config.upload_prefix}/submission_{submission_id}/{unique_id}{file_ext}"
            
            logger.info(f"📤 Generating pre-signed URL for: {upload_key}")
            
            # Generate pre-signed POST URL (for HTML form uploads)
            presigned_response = self.client.generate_presigned_post(
                Bucket=self.config.bucket_name,
                Key=upload_key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    ["content-length-range", 0, 52428800],  # 0-50MB
                    ["eq", "$Content-Type", content_type]
                ],
                ExpiresIn=self.config.presigned_url_ttl
            )
            
            # Also generate GET (download) URL for verification
            presigned_get_url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config.bucket_name, 'Key': upload_key},
                ExpiresIn=86400  # 24 hours for GET
            )
            
            # Construct public URL (after upload)
            if self.config.public_url_base:
                public_url = f"{self.config.public_url_base}/{upload_key}"
            else:
                # Fallback: use presigned GET URL
                public_url = presigned_get_url
            
            result = {
                'upload_url': presigned_response['url'],
                'public_url': public_url,
                'upload_key': upload_key,
                'expires_in': self.config.presigned_url_ttl,
                'form_data': presigned_response['fields'],  # For multipart/form-data
                'submission_id': submission_id
            }
            
            logger.info(f"✅ Pre-signed URL generated: {upload_key}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to generate pre-signed URL: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def validate_image_url(self, image_url: str, submission_id: int) -> bool:
        """
        Verify that image URL belongs to this submission's bucket path
        
        Security: Prevents directory traversal / unauthorized file access
        
        Args:
            image_url: URL to validate
            submission_id: Expected submission ID in path
        
        Returns:
            True if URL is valid and authorized, False otherwise
        """
        
        try:
            expected_path_segment = f"submission_{submission_id}"
            
            if expected_path_segment not in image_url:
                logger.warning(f"⚠️  Image URL doesn't match submission ID: {image_url}")
                return False
            
            # Additional check: ensure it's in our bucket
            if self.config.bucket_name not in image_url and self.config.endpoint_url not in image_url:
                logger.warning(f"⚠️  Image URL not from authorized bucket: {image_url}")
                return False
            
            logger.info(f"✅ Image URL validated: {image_url}")
            return True
        
        except Exception as e:
            logger.error(f"❌ URL validation error: {e}")
            return False
    
    def delete_image(self, upload_key: str) -> bool:
        """
        Delete an uploaded image from cloud storage
        
        Useful for cleanup after analysis or if user cancels
        
        Args:
            upload_key: Full key path (e.g., 'design-diagnosis/uploads/...')
        
        Returns:
            True if deleted, False if error
        """
        
        if not self.client:
            logger.warning("⚠️  Cloud storage not available")
            return False
        
        try:
            self.client.delete_object(Bucket=self.config.bucket_name, Key=upload_key)
            logger.info(f"✅ Deleted: {upload_key}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete {upload_key}: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """
        Health check: verify cloud storage connectivity
        
        Returns:
            True if bucket is accessible, False otherwise
        """
        
        if not self.client:
            return False
        
        try:
            self.client.head_bucket(Bucket=self.config.bucket_name)
            logger.info(f"✅ Cloud storage health check passed: {self.config.bucket_name}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Cloud storage health check failed: {e}")
            return False


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_cloud_manager = None

def get_cloud_manager() -> CloudStorageManager:
    """Get or initialize the global cloud storage manager"""
    global _cloud_manager
    if _cloud_manager is None:
        _cloud_manager = CloudStorageManager()
    return _cloud_manager


def get_cloud_config() -> CloudStorageConfig:
    """Get cloud storage configuration"""
    return get_cloud_manager().config
