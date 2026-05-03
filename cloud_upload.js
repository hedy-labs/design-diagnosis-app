/**
 * Cloud Storage Upload Helper
 * Handles direct browser uploads to S3/R2 buckets via pre-signed URLs
 */

class CloudUploadManager {
    constructor() {
        this.uploadedImages = [];  // Track successfully uploaded image URLs
        this.isCloudEnabled = true;  // Assume cloud enabled unless proven otherwise
    }

    /**
     * Request a pre-signed URL from backend
     * @param {number} submissionId - Form submission ID
     * @param {File} file - File object from input
     * @returns {Promise<Object>} Pre-signed URL info
     */
    async getPresignedUrl(submissionId, file) {
        try {
            console.log('📤 Requesting pre-signed URL from backend...');

            const response = await fetch('/api/presigned-upload-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    submission_id: submissionId,
                    filename: file.name,
                    content_type: file.type || 'image/jpeg'
                })
            });

            if (!response.ok) {
                const error = await response.json();
                if (response.status === 503) {
                    console.warn('⚠️  Cloud storage unavailable, fallback to server upload');
                    this.isCloudEnabled = false;
                    return null;
                }
                throw new Error(error.error || 'Failed to get pre-signed URL');
            }

            const data = await response.json();
            console.log('✅ Pre-signed URL received');
            return data;

        } catch (error) {
            console.error('❌ Error getting pre-signed URL:', error);
            this.isCloudEnabled = false;
            return null;
        }
    }

    /**
     * Upload file directly to cloud bucket using pre-signed URL
     * @param {File} file - File to upload
     * @param {Object} presignedInfo - Info from getPresignedUrl()
     * @returns {Promise<string>} Final image URL after successful upload
     */
    async uploadToCloud(file, presignedInfo) {
        if (!presignedInfo) {
            return null;
        }

        try {
            console.log(`📸 Uploading ${file.name} to cloud storage...`);

            // Create FormData with all presigned fields
            const formData = new FormData();
            
            // Add all form fields from presigned response
            for (const [key, value] of Object.entries(presignedInfo.form_data)) {
                formData.append(key, value);
            }
            
            // Add the file itself (MUST be last)
            formData.append('file', file);

            // POST to presigned URL (cloud bucket)
            const response = await fetch(presignedInfo.upload_url, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
            }

            console.log('✅ File uploaded to cloud storage');
            
            // Return the public URL where the file is now accessible
            return presignedInfo.public_url;

        } catch (error) {
            console.error('❌ Cloud upload error:', error);
            return null;
        }
    }

    /**
     * Upload a single image file (cloud or fallback)
     * @param {number} submissionId - Form submission ID
     * @param {File} file - File from input
     * @returns {Promise<string>} Final image URL (cloud or server)
     */
    async uploadImage(submissionId, file) {
        // Try cloud upload first
        if (this.isCloudEnabled) {
            const presigned = await this.getPresignedUrl(submissionId, file);
            if (presigned) {
                const cloudUrl = await this.uploadToCloud(file, presigned);
                if (cloudUrl) {
                    this.uploadedImages.push(cloudUrl);
                    return cloudUrl;
                }
            }
        }

        // Fallback: server-side upload (old behavior)
        console.log('⚠️  Falling back to server-side upload...');
        return await this.uploadToServerFallback(submissionId, file);
    }

    /**
     * Fallback: Upload to server (old method)
     * @param {number} submissionId - Form submission ID
     * @param {File} file - File to upload
     * @returns {Promise<string>} Data URI
     */
    async uploadToServerFallback(submissionId, file) {
        return new Promise((resolve, reject) => {
            try {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const dataUri = e.target.result;
                    console.log('✅ File loaded as data URI (server fallback)');
                    this.uploadedImages.push(dataUri);
                    resolve(dataUri);
                };
                reader.onerror = reject;
                reader.readAsDataURL(file);
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Get all uploaded image URLs
     * @returns {Array<string>} URLs ready for analysis
     */
    getUploadedImages() {
        return this.uploadedImages;
    }

    /**
     * Clear uploaded images (for reset/retry)
     */
    clearUploadedImages() {
        this.uploadedImages = [];
    }

    /**
     * Health check: Verify cloud storage availability
     * @returns {Promise<boolean>}
     */
    async checkCloudHealth() {
        try {
            const response = await fetch('/api/presigned-upload-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    submission_id: 0,
                    filename: 'test.jpg',
                    content_type: 'image/jpeg'
                })
            });

            if (response.status === 404) {
                // Submission not found, but endpoint exists = cloud healthy
                return true;
            }

            if (response.status === 503) {
                // Cloud storage unavailable
                return false;
            }

            return true;
        } catch (error) {
            console.warn('⚠️  Cloud health check failed:', error);
            return false;
        }
    }
}

// Export for use in form.html
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CloudUploadManager;
}
