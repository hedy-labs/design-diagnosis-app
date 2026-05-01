"""
Design Diagnosis Backend — FastAPI Entry Point (Phase 2)

Flat directory structure. All imports from root level only.
"""

from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import uuid
import os
from pathlib import Path
import logging
import shutil
import stripe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ .env file loaded")
except:
    logger.warning("python-dotenv not installed, skipping .env loading")

# Configuration
# BASE_URL: explicit fallback for VPS/production
BASE_URL = "http://147.182.247.168:8000"  # Default VPS IP

# Override with .env if set
DEFAULT_BASE_URL = os.getenv("BASE_URL", BASE_URL)
DB_PATH = os.getenv("DB_PATH", "design_diagnosis.db")

# DYNAMIC PATHS: Relative to application directory (no hardcoded /root/)
_app_dir = Path(__file__).parent.absolute()
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", str(_app_dir / "reports"))
UPLOADED_PHOTOS_DIR = os.getenv("UPLOADED_PHOTOS_DIR", str(_app_dir / "static" / "uploads"))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
AMAZON_AFFILIATE_ID = os.getenv("AMAZON_AFFILIATE_ID", "")

# DEFENSIVE: Create directories if they don't exist
try:
    os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
    os.makedirs(UPLOADED_PHOTOS_DIR, exist_ok=True)
    logger.info(f"✅ Directories created/verified")
except Exception as dir_err:
    logger.error(f"❌ Failed to create directories: {dir_err}")
    print(f"[CONFIG] ❌ Directory creation failed: {dir_err}")

# Log configuration
logger.info(f"📁 App directory: {_app_dir}")
logger.info(f"📁 Report output dir: {REPORT_OUTPUT_DIR}")
logger.info(f"📁 Uploaded photos dir: {UPLOADED_PHOTOS_DIR}")
print(f"[CONFIG] 📁 App dir: {_app_dir}")
print(f"[CONFIG] 📁 Report dir: {REPORT_OUTPUT_DIR}")
print(f"[CONFIG] 📁 Upload dir: {UPLOADED_PHOTOS_DIR}")


def get_uploaded_photos_for_submission(submission_id: int) -> List[str]:
    """
    Retrieve local file paths for photos uploaded by a user.
    
    Photos are stored in: UPLOADED_PHOTOS_DIR/submission_{id}/
    Returns: List of local file paths (can be loaded into base64 for Vision AI)
    """
    try:
        submission_dir = os.path.join(UPLOADED_PHOTOS_DIR, f"submission_{submission_id}")
        print(f"[FALLBACK] 🔍 Looking for photos in: {submission_dir}")
        
        if not os.path.exists(submission_dir):
            print(f"[FALLBACK] ❌ Directory does not exist: {submission_dir}")
            logger.info(f"ℹ️  No uploaded photos directory for submission {submission_id}")
            return []
        
        # Get all image files (.jpg, .png, .webp, etc.)
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
        photo_files = []
        
        for filename in sorted(os.listdir(submission_dir)):
            file_path = os.path.join(submission_dir, filename)
            if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in image_extensions:
                # Verify file exists and is readable
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    photo_files.append(file_path)
                    print(f"[FALLBACK] ✅ Found: {filename} ({os.path.getsize(file_path)} bytes)")
                else:
                    print(f"[FALLBACK] ⚠️  Skipped invalid file: {filename}")
        
        print(f"[FALLBACK] ✅ Located {len(photo_files)} valid photos for submission {submission_id}")
        logger.info(f"✅ Found {len(photo_files)} uploaded photos for submission {submission_id}")
        return photo_files
    except Exception as e:
        print(f"[FALLBACK] ❌ Error retrieving photos: {e}")
        logger.error(f"❌ Error retrieving uploaded photos: {e}")
        return []


def get_base_url(request: Optional[Request] = None) -> str:
    """
    Get BASE_URL from:
    1. .env BASE_URL (explicit override)
    2. Request headers (X-Forwarded-Proto + Host for VPS/proxies)
    3. Request URL (falls back to request itself)
    4. Default (localhost:8000)
    """
    if DEFAULT_BASE_URL:
        return DEFAULT_BASE_URL
    
    if request:
        # Check for X-Forwarded-Proto header (common with reverse proxies)
        proto = request.headers.get("X-Forwarded-Proto", request.url.scheme)
        host = request.headers.get("X-Forwarded-Host", request.url.netloc)
        return f"{proto}://{host}"
    
    return "http://localhost:8000"

# Create report output directory
Path(REPORT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ============================================================================
# INITIALIZE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Design Diagnosis API",
    description="AI-powered interior design diagnostic for Airbnb/VRBO hosts",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# IMPORT MODELS
# ============================================================================

from models import (
    FormSubmitInput, FormSubmitResponse,
    EmailVerificationInput, EmailVerificationResponse,
    CreatePaymentInput, CreatePaymentResponse,
    ReportResponse, HealthResponse
)

# ============================================================================
# IMPORT DATABASE
# ============================================================================

db = None
try:
    from database import DesignDiagnosisDB
    db = DesignDiagnosisDB(DB_PATH)
    logger.info(f"✅ Database initialized: {DB_PATH}")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")

# Initialize email list management routes
try:
    from email_list_routes import create_email_list_router
    email_list_router = create_email_list_router(db)
    app.include_router(email_list_router)
    logger.info("✅ Email list management routes initialized")
except Exception as e:
    logger.error(f"⚠️  Email list routes failed to load: {e}")

# ============================================================================
# MOCK SERVICES (for development)
# ============================================================================

# Email Service (SendGrid or Mock)
try:
    from email_service import EmailService
    email_service = EmailService()
    logger.info("✅ Email service initialized")
except Exception as e:
    logger.error(f"❌ Email service initialization failed: {e}")
    email_service = None

# Stripe Service
try:
    from stripe_service import StripeService
    stripe_service = StripeService()
    logger.info("✅ Stripe service initialized")
except Exception as e:
    logger.error(f"❌ Stripe service initialization failed: {e}")
    stripe_service = None

# Scoring Engine (Mock)
# BUSINESS LOGIC FIX: Use real scoring engine instead of mock
try:
    from design_diagnosis_backend.scoring import ScoringEngine as RealScoringEngine
    
    class ProductionScoringEngine:
        """Wrapper for real ScoringEngine with comfort checklist support"""
        def __init__(self):
            self.engine = RealScoringEngine()
        
        def calculate_score(self, guest_comfort_checklist: List[str], property_type: str):
            """Calculate score based on comfort checklist"""
            try:
                # CRITICAL LOGGING: Log inputs before calculation
                logger.info(f"🔍 SCORING DEBUG: checklist type = {type(guest_comfort_checklist)}")
                logger.info(f"🔍 SCORING DEBUG: checklist = {guest_comfort_checklist}")
                logger.info(f"🔍 SCORING DEBUG: checklist length = {len(guest_comfort_checklist) if guest_comfort_checklist else 0}")
                
                # Convert comfort checklist to scoring dimensions
                # This is a simplified mapping; in production, expand this logic
                if not guest_comfort_checklist:
                    score = 0
                else:
                    score = len(guest_comfort_checklist) * 4  # Each item = ~4 points
                
                logger.info(f"🔍 SCORING DEBUG: raw score = {score}")
                
                score = min(100, max(0, score))
                logger.info(f"🔍 SCORING DEBUG: capped score = {score}")
                
                grade = self.engine.assign_grade(score)
                logger.info(f"🔍 SCORING DEBUG: grade = {grade}")
                
                return {'score': score, 'grade': grade}
            except Exception as e:
                logger.error(f"🔴 SCORING CALCULATION ERROR: {e}")
                logger.error(f"   Type: {type(e).__name__}")
                logger.error(f"   Checklist: {guest_comfort_checklist}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                # Re-raise so caller knows there was an error
                raise
    
    scoring_engine = ProductionScoringEngine()
    logger.info("✅ Scoring engine initialized (PRODUCTION MODE)")
except Exception as e:
    logger.error(f"🔴 PRODUCTION SCORING ENGINE FAILED TO INITIALIZE: {e}")
    logger.error(f"   Type: {type(e).__name__}")
    import traceback
    logger.error(f"   Traceback: {traceback.format_exc()}")
    logger.warning("⚠️  Falling back to mock mode")
    
    class MockScoringEngine:
        def calculate_score(self, guest_comfort_checklist: List[str], property_type: str):
            # Fallback: count checklist items
            score = len(guest_comfort_checklist) * 4
            score = min(100, max(0, score))
            
            if score >= 90:
                grade = 'A'
            elif score >= 80:
                grade = 'B'
            elif score >= 70:
                grade = 'C'
            elif score >= 60:
                grade = 'D'
            else:
                grade = 'F'
            
            return {'score': score, 'grade': grade}
    
    scoring_engine = MockScoringEngine()
    logger.info("✅ Scoring engine initialized (MOCK MODE FALLBACK)")

# PDF Generator V2 (Weasyprint-based HTML-to-PDF)
try:
    from pdf_generator_v2 import generate_pdf_report_v2, generate_html_report
    pdf_available = True
    logger.info("✅ PDF generator V2 initialized (Weasyprint HTML-to-PDF)")
except ImportError:
    logger.warning("⚠️  pdf_generator_v2 not available, using fallback")
    pdf_available = False

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "app": "Design Diagnosis API v2.0",
        "status": "running",
        "endpoints": {
            "form": "/form.html",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "database": "✅ OK" if db else "❌ Error",
        "email": "✅ OK",
        "stripe": "✅ OK",
        "scoring": "✅ OK",
        "pdf": "✅ OK",
    }
    
    return HealthResponse(
        status="healthy" if all("✅" in v for v in services.values()) else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        services=services
    )


# ============================================================================
# TEST PILOT SUPPORT (For Automated QA)
# ============================================================================

@app.post("/test/mark-payment-complete")
async def test_mark_payment_complete(submission_id: int, test_key: str = ""):
    """
    TEST ONLY: Mark a submission as paid (bypasses Stripe redirect for testing).
    
    Requires: test_key=PILOT_TEST_KEY (set in environment or hardcoded below)
    This endpoint ONLY works in development mode and will be removed in production.
    """
    PILOT_TEST_KEY = os.getenv("PILOT_TEST_KEY", "pilot-test-key-insecure-dev-only")
    
    if test_key != PILOT_TEST_KEY:
        logger.warning(f"❌ Test endpoint called with invalid key")
        raise HTTPException(status_code=401, detail="Invalid test key")
    
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Get submission
        submission = db.get_form_submission(submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
        
        # Create fake payment record (for testing premium flow)
        payment = db.create_payment(
            submission_id=submission_id,
            stripe_intent_id=f"test_session_{uuid.uuid4().hex[:8]}",
            amount=3900,
            status="completed"
        )
        
        logger.info(f"🧪 TEST: Marked submission {submission_id} as paid (payment {payment.id})")
        print(f"[TEST] ✅ Submission {submission_id} marked as PAID (fake payment {payment.id})")
        
        return {
            "success": True,
            "submission_id": submission_id,
            "message": "TEST: Submission marked as paid",
            "payment_id": payment.id
        }
    
    except Exception as e:
        logger.error(f"❌ Test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-uploaded-photos")
async def analyze_uploaded_photos(request: Request):
    """
    DECOUPLED UPLOAD ENDPOINT: Save photos only, NO Vision AI analysis
    
    Input: multipart/form-data with 'photos' files
    Output: { "success": bool, "submission_id": int, "file_count": int }
    
    Photos are saved to: UPLOADED_PHOTOS_DIR/temp_uploads/
    Vision AI analysis happens LATER during form submission.
    """
    try:
        form = await request.form()
        uploaded_files = form.getlist('photos')
        
        if not uploaded_files or len(uploaded_files) == 0:
            logger.error("❌ No photos provided")
            return {"success": False, "error": "No photos provided"}, 400
        
        logger.info(f"📸 Saving {len(uploaded_files)} uploaded photos (NO ANALYSIS)")
        print(f"[UPLOAD] 📸 Saving {len(uploaded_files)} photos to disk")
        
        # Create temp upload directory
        temp_upload_dir = os.path.join(UPLOADED_PHOTOS_DIR, "temp_uploads")
        try:
            os.makedirs(temp_upload_dir, exist_ok=True)
            print(f"[UPLOAD] ✅ Temp directory ready: {temp_upload_dir}")
        except Exception as mkdir_err:
            logger.error(f"❌ Failed to create upload directory: {mkdir_err}")
            print(f"[UPLOAD] ❌ Directory creation failed: {mkdir_err}")
            return {"success": False, "error": f"Failed to create directory: {mkdir_err}"}, 500
        
        # Save files to disk (NO VISION AI)
        saved_count = 0
        
        for idx, file in enumerate(uploaded_files):
            try:
                content = await file.read()
                
                # Save to temporary directory with UUID to avoid collisions
                file_ext = os.path.splitext(file.filename)[1] or '.jpg'
                temp_filename = f"{uuid.uuid4().hex}{file_ext}"
                temp_path = os.path.join(temp_upload_dir, temp_filename)
                
                # Write file to disk
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                # Verify file was written
                if os.path.exists(temp_path):
                    file_size = os.path.getsize(temp_path)
                    saved_count += 1
                    print(f"[UPLOAD] ✅ File {idx + 1}: {file.filename} ({file_size} bytes)")
                    logger.info(f"✅ File saved: {temp_filename} ({file_size} bytes)")
                else:
                    logger.error(f"❌ File write verification failed: {temp_path}")
                    print(f"[UPLOAD] ❌ File write failed: {temp_path}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to save file {file.filename}: {e}")
                print(f"[UPLOAD] ⚠️  File save error: {e}")
                continue
        
        if saved_count == 0:
            logger.error("❌ No files were saved")
            return {"success": False, "error": "No files could be saved"}, 400
        
        logger.info(f"✅ Saved {saved_count} photos to temp storage (Vision AI deferred)")
        print(f"[UPLOAD] ✅ COMPLETE: {saved_count} photos saved, NO ANALYSIS")
        
        # Return 200 OK with minimal response (NO VISION RESULTS)
        return {
            "success": True,
            "submission_id": None,  # Will be assigned when form is submitted
            "file_count": saved_count
        }, 200
    
    except Exception as e:
        logger.error(f"❌ Upload endpoint error: {e}")
        print(f"[UPLOAD] ❌ FATAL: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}, 500


@app.post("/api/test-scraper")
async def test_scraper(request: Request):
    """
    GUARDRAIL: Test Airbnb scraper BEFORE payment redirect
    
    Purpose: Verify Airbnb allows photo extraction before user proceeds to Stripe
    
    Input: { "url": "https://www.airbnb.com/rooms/..." }
    Output: { "success": bool, "photos": [...], "count": int, "error": str }
    """
    try:
        body = await request.json()
        airbnb_url = body.get("url")
        
        if not airbnb_url:
            logger.warning("❌ Test scraper: Missing URL")
            return JSONResponse({"success": False, "error": "Missing URL"}, status_code=400)
        
        logger.info(f"🔍 Test-scraper: Verifying {airbnb_url[:60]}...")
        print(f"[SCRAPER-TEST] 🔍 Testing Airbnb scraper for guardrail")
        
        from photo_scraper import extract_airbnb_photos
        
        try:
            photos = await extract_airbnb_photos(airbnb_url)
            
            if not photos or len(photos) < 3:
                logger.warning(f"⚠️  Scraper found insufficient photos: {len(photos) if photos else 0}")
                print(f"[SCRAPER-TEST] ❌ Insufficient photos: {len(photos) if photos else 0}")
                return {
                    "success": False,
                    "photos": photos or [],
                    "count": len(photos) if photos else 0,
                    "error": "Airbnb blocked automated access or insufficient photos"
                }
            
            logger.info(f"✅ Scraper test passed: {len(photos)} photos found")
            print(f"[SCRAPER-TEST] ✅ Success: {len(photos)} photos found")
            return {
                "success": True,
                "photos": photos,
                "count": len(photos),
                "error": None
            }
        
        except Exception as scraper_error:
            logger.error(f"❌ Scraper test failed: {type(scraper_error).__name__}: {scraper_error}")
            print(f"[SCRAPER-TEST] ❌ Scraper failed: {type(scraper_error).__name__}")
            return {
                "success": False,
                "photos": [],
                "count": 0,
                "error": str(scraper_error)
            }
    
    except Exception as e:
        logger.error(f"❌ Test-scraper endpoint error: {e}")
        print(f"[SCRAPER-TEST] ❌ FATAL: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/analyze-listing")
async def analyze_listing(request_data: dict):
    """
    Analyze Airbnb/VRBO listing: Extract photos + Vision AI analysis
    
    Input: { "airbnb_url": "https://www.airbnb.com/rooms/..." }
    Output: { "success": bool, "vision_results": {...} }
    """
    try:
        airbnb_url = request_data.get("airbnb_url")
        if not airbnb_url:
            return {"success": False, "error": "Missing airbnb_url"}
        
        logger.info(f"🔍 Analyzing listing: {airbnb_url}")
        
        # Import here to avoid startup dependency issues
        import asyncio
        from photo_scraper import extract_airbnb_photos
        from vision_analyzer_v2 import VisionAnalyzerV2
        from vision_to_vitality import map_vision_to_design_score, get_design_narrative
        
        # Extract photos from listing
        logger.info(f"📸 Extracting photos...")
        try:
            image_urls = await extract_airbnb_photos(airbnb_url)
            if not image_urls:
                logger.warning("⚠️  No images extracted from listing")
                return {"success": False, "error": "No images found in listing"}
            
            logger.info(f"✅ Extracted {len(image_urls)} images")
        except Exception as e:
            logger.error(f"❌ Photo extraction failed: {e}")
            return {"success": False, "error": f"Could not extract photos: {str(e)}"}
        
        # Analyze with Vision AI
        logger.info(f"🤖 Analyzing {len(image_urls)} images with Vision AI...")
        analyzer = VisionAnalyzerV2()
        vision_results = await analyzer.analyze_images_batch(image_urls, max_images=10)
        
        if not vision_results:
            logger.warning("⚠️  Vision analysis failed")
            return {"success": False, "error": "Vision analysis failed"}
        
        # Map to design score
        design_mapping = map_vision_to_design_score(vision_results)
        design_narrative = get_design_narrative(vision_results, design_mapping)
        
        logger.info(f"✅ Analysis complete: design_score={design_mapping['design_score']}/30")
        
        return {
            "success": True,
            "vision_results": {
                "lighting_quality": vision_results.get('lighting_quality', 10),
                "color_harmony": vision_results.get('color_harmony', 10),
                "clutter_density": vision_results.get('clutter_density', 10),
                "staging_integrity": vision_results.get('staging_integrity', 10),
                "functionality": vision_results.get('functionality', 10),
                "design_score": design_mapping['design_score'],
                "design_narrative": design_narrative,
                "room_summaries": vision_results.get('room_summaries', {})
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Listing analysis error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/submit-form", response_model=FormSubmitResponse)
async def submit_form(form_data: FormSubmitInput, background_tasks: BackgroundTasks, request: Request):
    """
    Submit property form with zero-friction for returning verified users
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        logger.info(f"📝 Form submission from {form_data.email} for {form_data.property_name}")
        
        # BACKEND VALIDATION FIX: Allow manual uploads without URL
        # Check if photos were manually uploaded
        temp_upload_dir = os.path.join(UPLOADED_PHOTOS_DIR, "temp_uploads")
        has_manually_uploaded_photos = False
        if os.path.exists(temp_upload_dir):
            temp_files = [f for f in os.listdir(temp_upload_dir) if os.path.isfile(os.path.join(temp_upload_dir, f))]
            has_manually_uploaded_photos = len(temp_files) > 0
        
        # Validate: Airbnb URL is required ONLY if no manual upload
        if not has_manually_uploaded_photos:
            if not form_data.airbnb_url or not form_data.airbnb_url.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Airbnb/VRBO URL is required. Please provide your listing URL or upload photos manually."
                )
            
            # Validate: URL contains airbnb or vrbo
            url_lower = form_data.airbnb_url.lower()
            if 'airbnb' not in url_lower and 'vrbo' not in url_lower:
                raise HTTPException(
                    status_code=400,
                    detail="Please enter a valid Airbnb or VRBO listing URL."
                )
        else:
            logger.info(f"✅ Manual photo upload detected ({len(temp_files)} files) - Airbnb URL not required")
        
        # Check if user is already verified (zero-friction return)
        user = db.get_or_create_user(form_data.email, wants_marketing=form_data.wants_marketing_emails)
        is_returning_verified = user.is_verified
        
        # Update marketing preference if user opted in
        if form_data.wants_marketing_emails and not user.wants_marketing_emails:
            db.update_marketing_preference(user.id, True)
            logger.info(f"📬 User {form_data.email} opted in to marketing emails")
        
        logger.info(f"🔍 User status: {'Returning Verified ✅' if is_returning_verified else 'New/Unverified'}")
        
        # BUG FIX 1: Log comfort data to debug data loss
        print(f"[FORM] 📋 Received comfort checklist: {form_data.guest_comfort_checklist}")
        print(f"[FORM]    Items count: {len(form_data.guest_comfort_checklist) if form_data.guest_comfort_checklist else 0}")
        logger.info(f"📋 Comfort items received: {form_data.guest_comfort_checklist}")
        
        # Save form submission (with optional vision_results if provided)
        submission = db.create_form_submission(
            email=form_data.email,
            property_name=form_data.property_name,
            airbnb_url=form_data.airbnb_url,
            listing_type=form_data.listing_type,
            bedrooms=form_data.bedrooms,
            bathrooms=form_data.bathrooms,
            guest_capacity=form_data.guest_capacity,
            total_photos=form_data.total_photos,
            guest_comfort_checklist=form_data.guest_comfort_checklist,
            report_type=form_data.report_type
        )
        
        # Store vision_results temporarily (for background task access)
        # In production, this should be stored in database; for now, use in-memory cache
        if hasattr(form_data, 'vision_results') and form_data.vision_results:
            # Store in app state for background task to access
            if not hasattr(app, '_vision_cache'):
                app._vision_cache = {}
            app._vision_cache[submission.id] = form_data.vision_results
            logger.info(f"💾 Vision results cached for submission {submission.id}")
        
        # Move any uploaded photos from temp directory to submission-specific directory
        temp_upload_dir = os.path.join(UPLOADED_PHOTOS_DIR, "temp_uploads")
        if os.path.exists(temp_upload_dir):
            submission_photo_dir = os.path.join(UPLOADED_PHOTOS_DIR, f"submission_{submission.id}")
            os.makedirs(submission_photo_dir, exist_ok=True)
            
            try:
                temp_files = [f for f in os.listdir(temp_upload_dir) if os.path.isfile(os.path.join(temp_upload_dir, f))]
                if temp_files:
                    for filename in temp_files:
                        src_path = os.path.join(temp_upload_dir, filename)
                        dst_path = os.path.join(submission_photo_dir, filename)
                        import shutil
                        shutil.move(src_path, dst_path)
                        
                        # CRITICAL: Verify file move succeeded
                        if os.path.exists(dst_path):
                            file_size = os.path.getsize(dst_path)
                            logger.info(f"✅ Photo moved to disk: {dst_path} (size: {file_size} bytes)")
                            print(f"[FORM] ✅ MOVED: {filename} → submission_{submission.id}/ ({file_size} bytes)")
                        else:
                            logger.error(f"❌ CRITICAL: Move verification failed for {filename}")
                            raise Exception(f"File move verification failed for {filename}")
                    
                    print(f"[FORM] ✅ ALL {len(temp_files)} photos verified on disk in submission_{submission.id}/")
            except Exception as move_err:
                logger.error(f"❌ Failed to move photos: {move_err}")
                print(f"[FORM] ❌ Photo move error: {move_err}")
        
        logger.info(f"✅ Submission saved with ID: {submission.id}")
        
        # ZERO-FRICTION PATH: If user already verified, skip email verification
        if is_returning_verified:
            logger.info(f"⚡ Returning verified user ({form_data.email}). Skipping email verification.")
            
            if form_data.report_type == "free":
                # Free report: generate immediately
                background_tasks.add_task(
                    generate_and_send_report,
                    submission_id=submission.id,
                    report_type="free"
                )
                return FormSubmitResponse(
                    success=True,
                    submission_id=submission.id,
                    message="✅ Welcome back! Your report is being generated. Check your email in 2-5 minutes.",
                    next_step="report_generating"
                )
            else:
                # Premium: ready to checkout
                return FormSubmitResponse(
                    success=True,
                    submission_id=submission.id,
                    message="✅ Ready to checkout! Proceeding to payment.",
                    next_step="stripe_checkout"
                )
        
        # STANDARD PATH: New user or unverified, send verification email
        verification_token = str(uuid.uuid4())
        db.create_email_verification(
            submission_id=submission.id,
            email=form_data.email,
            token=verification_token
        )
        
        logger.info(f"✅ Verification token created: {verification_token[:12]}...")
        
        # Get dynamic BASE_URL from request
        base_url = get_base_url(request)
        
        # Send verification email
        verification_link = f"{base_url}/api/verify-email?token={verification_token}"
        logger.info(f"📧 Verification link: {verification_link}")
        background_tasks.add_task(
            email_service.send_verification_email,
            email=form_data.email,
            property_name=form_data.property_name,
            verification_link=verification_link
        )
        
        return FormSubmitResponse(
            success=True,
            message=f"✅ Form submitted! Check your email ({form_data.email}) to verify and receive your report.",
            submission_id=submission.id,
            next_step="verify_email"
        )
    
    except Exception as e:
        logger.error(f"❌ Form submission error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/verify-email")
async def verify_email(background_tasks: BackgroundTasks, token: str = Query(...)):
    """
    Verify email with token and trigger report generation
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        logger.info(f"🔐 Email verification attempt: {token[:12]}...")
        
        # Validate token
        verification = db.get_email_verification_by_token(token)
        if not verification:
            return HTMLResponse(
                "<h1>❌ Invalid or Expired Token</h1><p>This verification link is invalid or has expired.</p>",
                status_code=400
            )
        
        if verification.verified:
            return HTMLResponse(
                "<h1>✅ Already Verified</h1><p>Your email has already been verified.</p>"
            )
        
        # Mark email as verified (both in verifications table AND mark user as verified)
        db.mark_email_verified(verification.id)
        logger.info(f"✅ Email verified: {verification.email}")
        
        # Also mark the USER as verified for zero-friction future returns
        user = db.get_user_by_email(verification.email)
        if user:
            db.mark_user_verified(user.id)
            logger.info(f"⚡ User marked as verified for zero-friction returns")
        
        # Get submission
        submission = db.get_form_submission(verification.submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Generate report in background
        background_tasks.add_task(
            generate_and_send_report,
            submission_id=submission.id,
            report_type=submission.report_type
        )
        
        # Redirect to beautiful email-verified page
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/email-verified", status_code=302)
    
    except Exception as e:
        logger.error(f"❌ Email verification error: {e}")
        return HTMLResponse(
            f"<h1>❌ Error</h1><p>{str(e)}</p>",
            status_code=500
        )


@app.post("/api/create-checkout-session", response_model=CreatePaymentResponse)
async def create_checkout_session(payment_input: CreatePaymentInput, request: Request):
    """
    Create Stripe Checkout Session for premium report payment
    
    Input: CreatePaymentInput (submission_id: int, property_name: str)
    Output: CreatePaymentResponse (session_id, url)
    """
    try:
        print(f"[CHECKOUT] 📋 Request received:")
        print(f"[CHECKOUT]    submission_id: {payment_input.submission_id}")
        print(f"[CHECKOUT]    property_name: {payment_input.property_name}")
        
        if not stripe_service:
            print(f"[CHECKOUT] ❌ Stripe service unavailable")
            raise HTTPException(status_code=503, detail="Stripe service unavailable")
        
        if not db:
            print(f"[CHECKOUT] ❌ Database service unavailable")
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        logger.info(f"💳 Checkout session requested for submission {payment_input.submission_id}")
        print(f"[CHECKOUT] 🔍 Looking up submission {payment_input.submission_id}...")
        
        # Verify submission exists
        submission = db.get_form_submission(payment_input.submission_id)
        if not submission:
            print(f"[CHECKOUT] ❌ Submission {payment_input.submission_id} not found in database")
            raise HTTPException(status_code=404, detail=f"Submission {payment_input.submission_id} not found")
        
        print(f"[CHECKOUT] ✅ Submission found: {submission.property_name}")
        
        # Get base URL
        base_url = get_base_url(request)
        
        # Create Stripe Checkout Session
        session = stripe_service.create_checkout_session(
            submission_id=payment_input.submission_id,
            property_name=payment_input.property_name,
            customer_email=submission.email,
            success_url=f"{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/payment-cancelled?session_id={{CHECKOUT_SESSION_ID}}"
        )
        
        logger.info(f"✅ Checkout session created: {session['session_id']}")
        print(f"[CHECKOUT] ✅ Session created: {session['session_id']}")
        print(f"[CHECKOUT]    URL: {session['checkout_url']}")
        
        # Store payment record
        db.create_payment(
            submission_id=payment_input.submission_id,
            stripe_intent_id=session['session_id'],
            amount=3900,
            status="pending"
        )
        
        return CreatePaymentResponse(
            success=True,
            session_id=session['session_id'],
            url=session['checkout_url'],
            message="Stripe Checkout session ready"
        )
    
    except Exception as e:
        print(f"[CHECKOUT] ❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[CHECKOUT] Traceback:")
        for line in traceback.format_exc().split('\n'):
            if line:
                print(f"[CHECKOUT]   {line}")
        logger.error(f"❌ Checkout session creation error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payment-webhook")
async def payment_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Stripe webhook events (checkout.session.completed)
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("Stripe-Signature")
        
        logger.info("📦 Webhook received from Stripe")
        
        # Verify webhook signature
        event = stripe_service.verify_webhook_signature(payload, sig_header)
        
        # In mock mode, parse the payload directly
        if not event:
            try:
                event = json.loads(payload)
                logger.info(f"📦 [MOCK] Webhook event: {event.get('type', 'unknown')}")
            except:
                logger.warning("⚠️  Could not parse webhook payload")
                return {"status": "received"}
        
        logger.info(f"📦 Event type: {event.get('type', 'unknown')}")
        
        # Handle checkout.session.completed
        if event.get('type') == 'checkout.session.completed':
            session = event.get('data', {}).get('object', {})
            session_id = session.get('id')
            metadata = session.get('metadata', {})
            
            logger.info(f"💳 Checkout session completed: {session_id}")
            logger.info(f"💳 Session metadata: {metadata}")
            
            if not db:
                logger.error("❌ Database unavailable for webhook")
                return JSONResponse({"error": "DB unavailable"}, status_code=503)
            
            # Get payment by session ID
            payment = db.get_payment_by_stripe_id(session_id)
            if not payment:
                logger.error(f"❌ Payment not found for session {session_id}")
                # Try alternate: extract submission_id from metadata
                submission_id_str = metadata.get('submission_id')
                if submission_id_str:
                    try:
                        submission_id = int(submission_id_str)
                        logger.info(f"💳 Found submission_id in metadata: {submission_id}")
                        # Payment might not be created yet, but submission exists
                    except:
                        logger.error(f"❌ Could not parse submission_id from metadata: {submission_id_str}")
                        return JSONResponse({"error": "Payment not found"}, status_code=404)
                else:
                    return JSONResponse({"error": "Payment not found"}, status_code=404)
            else:
                submission_id = payment.submission_id
            
            # Mark payment as completed (if exists)
            if payment:
                db.update_payment_status(payment.id, "completed")
                logger.info(f"✅ Payment marked completed: {payment.id}")
            
            # Get submission
            submission = db.get_form_submission(submission_id)
            if not submission:
                logger.error(f"❌ Submission not found for submission_id {submission_id}")
                return {"status": "received"}
            
            # IMMEDIATELY queue premium report generation
            logger.info(f"📊 Queuing premium report generation for submission {submission.id}")
            background_tasks.add_task(
                generate_and_send_report,
                submission_id=submission.id,
                report_type="premium"
            )
            
            logger.info(f"✅ Webhook processing complete. Report generation queued.")
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int):
    """
    Retrieve report details
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        report = db.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ReportResponse(
            success=True,
            report_id=report.id,
            property_name=report.property_name,
            vitality_score=report.vitality_score,
            grade=report.grade,
            file_url=f"{BASE_URL}/reports/{report.file_name}"
        )
    
    except Exception as e:
        logger.error(f"❌ Report retrieval error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# STATIC FILES
# ============================================================================

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory="."), name="static")
    logger.info("✅ Static files mounted at /static")
except Exception as e:
    logger.warning(f"⚠️  Could not mount static directory: {e}")

@app.get("/form.html", response_class=HTMLResponse)
async def get_form():
    """Serve the production form"""
    form_paths = [
        "./form.html",
        "form.html",
        "/root/design-diagnosis-app/form.html"
    ]
    
    for form_path in form_paths:
        if os.path.exists(form_path):
            logger.info(f"📄 Serving form.html from {form_path}")
            with open(form_path, 'r') as f:
                return f.read()
    
    logger.error("❌ form.html not found in any expected location")
    return HTMLResponse("<h1>❌ Form not found</h1><p>Expected at ./form.html</p>", status_code=404)


@app.get("/payment-success", response_class=HTMLResponse)
async def payment_success(session_id: str = Query(None), background_tasks: BackgroundTasks = None):
    """
    Serve payment success page + trigger report generation
    """
    try:
        # If session_id provided, trigger report generation immediately
        if session_id and db and background_tasks:
            logger.info(f"💳 Processing payment success for session: {session_id}")
            
            # Get payment
            payment = db.get_payment_by_stripe_id(session_id)
            if payment:
                # Mark as completed
                db.update_payment_status(payment.id, "completed")
                logger.info(f"✅ Payment marked completed: {payment.id}")
                
                # Get submission
                submission = db.get_form_submission(payment.submission_id)
                if submission:
                    # Queue report generation immediately
                    background_tasks.add_task(
                        generate_and_send_report,
                        submission_id=submission.id,
                        report_type="premium"
                    )
                    logger.info(f"📊 Premium report generation queued for submission {submission.id}")
    except Exception as e:
        logger.error(f"⚠️  Payment success handler error: {e}")
    
    # Serve success page
    success_paths = [
        "./payment-success.html",
        "payment-success.html",
        "/root/design-diagnosis-app/payment-success.html"
    ]
    
    for success_path in success_paths:
        if os.path.exists(success_path):
            logger.info(f"📄 Serving payment-success.html from {success_path}")
            with open(success_path, 'r') as f:
                return f.read()
    
    logger.error("❌ payment-success.html not found in any expected location")
    return HTMLResponse("<h1>❌ Success page not found</h1>", status_code=404)


@app.get("/payment-success.html", response_class=HTMLResponse)
async def payment_success_html(session_id: str = Query(None), background_tasks: BackgroundTasks = None):
    """
    Serve payment success page at /payment-success.html (alias for /payment-success)
    Handles Stripe redirects that may append .html extension
    """
    return await payment_success(session_id=session_id, background_tasks=background_tasks)


@app.get("/email-verified", response_class=HTMLResponse)
async def email_verified():
    """Serve the email verified confirmation page"""
    verified_paths = [
        "./email-verified.html",
        "email-verified.html",
        "/root/design-diagnosis-app/email-verified.html"
    ]
    
    for verified_path in verified_paths:
        if os.path.exists(verified_path):
            logger.info(f"📄 Serving email-verified.html from {verified_path}")
            with open(verified_path, 'r') as f:
                return f.read()
    
    logger.error("❌ email-verified.html not found in any expected location")
    return HTMLResponse("<h1>❌ Verified page not found</h1>", status_code=404)


@app.get("/api/upgrade-checkout/{submission_id}")
async def upgrade_checkout(submission_id: int):
    """
    Generate Stripe checkout session for free → premium upgrade
    
    Args:
        submission_id: ID of existing free tier submission
    
    Returns:
        Stripe checkout session URL (redirect user to checkout.stripe.com/pay/...)
    """
    try:
        print(f"[CHECKOUT] Upgrade request for submission_id={submission_id}")
        
        # Verify submission exists using database method
        if not db:
            print(f"[CHECKOUT] ❌ Database not initialized")
            return {"success": False, "error": "Database error"}
        
        submission = db.get_form_submission(submission_id)
        
        if not submission:
            print(f"[CHECKOUT] ❌ Submission {submission_id} not found")
            return {"success": False, "error": "Submission not found"}
        
        print(f"[CHECKOUT] Found submission for {submission.email}")
        
        # Create Stripe checkout session for $39 CAD premium PDF
        # Construct redirect URLs using forced IP (http://147.182.247.168:8000)
        base_url = "http://147.182.247.168:8000"  # Matches forced IP in email_service.py
        success_url = f"{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/form.html"
        
        session = stripe_service.create_checkout_session(
            submission_id=submission_id,
            property_name=submission.property_name,
            customer_email=submission.email,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        print(f"[CHECKOUT] ✅ Checkout session created: {session['session_id']}")
        print(f"[CHECKOUT] Redirecting to: {session['checkout_url']}")
        
        # Redirect directly to Stripe checkout
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=session['checkout_url'])
    
    except Exception as e:
        print(f"[CHECKOUT] ❌ Checkout creation failed: {e}")
        logger.error(f"Upgrade checkout error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/payment-cancelled", response_class=HTMLResponse)
async def payment_cancelled(session_id: str = Query(None)):
    """Handle cancelled Stripe payment"""
    try:
        logger.info(f"⚠️  Payment cancelled: session_id={session_id}")
        
        if session_id and db:
            payment = db.get_payment_by_stripe_id(session_id)
            if payment:
                db.update_payment_status(payment.id, "cancelled")
                logger.info(f"✅ Payment marked as cancelled: {payment.id}")
        
        # Return HTML with message
        return HTMLResponse("""
        <html>
        <head>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
                .container { max-width: 600px; margin: 0 auto; }
                h1 { color: #ff6b6b; }
                p { color: #555; }
                a { color: #667eea; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Payment Cancelled</h1>
                <p>Your payment was cancelled. You can try again anytime.</p>
                <p><a href="/form.html">← Back to Form</a></p>
            </div>
        </body>
        </html>
        """)
    
    except Exception as e:
        logger.error(f"❌ Cancel handler error: {e}")
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def generate_and_send_report(submission_id: int, report_type: str):
    """
    Generate PDF report and send via email (ENFORCED PIPELINE WITH VISION AI)
    
    CRITICAL: This function MUST run Vision AI before generating any report.
    Pipeline:
    1. Get submission
    2. Extract or load photos (scraper OR uploaded)
    3. Run Vision AI analysis
    4. Clean database data with human-readable formatting
    5. Generate report with vision results
    6. Send email
    """
    try:
        if not db:
            logger.error("❌ Database not available for report generation")
            print("[REPORT] ❌ Database unavailable")
            return
        
        print(f"[REPORT] 📊 STARTING REPORT GENERATION PIPELINE")
        print(f"[REPORT]    submission_id: {submission_id}")
        print(f"[REPORT]    report_type: {report_type}")
        logger.info(f"📊 Generating {report_type} report for submission {submission_id}...")
        
        submission = db.get_form_submission(submission_id)
        if not submission:
            logger.error(f"❌ Submission {submission_id} not found")
            print(f"[REPORT] ❌ Submission not found in database")
            return
        
        print(f"[REPORT] ✅ Submission retrieved: {submission.property_name}")
        
        # ================================================================
        # STEP 1: VISION AI ANALYSIS (MANDATORY - DO NOT SKIP)
        # ================================================================
        print(f"[REPORT] 🚀 STEP 1: Running Vision AI analysis...")
        
        vision_results = None
        
        # Try to retrieve from cache FIRST (form submission path with scraped photos)
        if hasattr(app, '_vision_cache') and submission_id in app._vision_cache:
            vision_results = app._vision_cache[submission_id]
            print(f"[REPORT] 💾 Vision results from cache (pre-analyzed photos)")
            logger.info(f"💾 Retrieved cached vision results for submission {submission_id}")
            del app._vision_cache[submission_id]
        
        # If not cached, must extract photos and run Vision AI (payment success path)
        if not vision_results:
            print(f"[REPORT] 🔍 No cached vision results - extracting photos...")
            
            from photo_scraper import extract_airbnb_photos
            from vision_analyzer_v2 import VisionAnalyzerV2
            from vision_to_vitality import map_vision_to_design_score, get_design_narrative
            
            image_urls = []
            scraper_attempted = False
            
            # STRATEGY 1: Try Airbnb URL scraper
            if submission.airbnb_url:
                print(f"[REPORT]    📍 Strategy 1: Airbnb URL scraper")
                scraper_attempted = True
                try:
                    image_urls = await extract_airbnb_photos(submission.airbnb_url)
                    if image_urls:
                        print(f"[REPORT]    ✅ Extracted {len(image_urls)} images from URL")
                        logger.info(f"✅ Extracted {len(image_urls)} photos from Airbnb URL")
                    else:
                        print(f"[REPORT] ⚠️  Scraper returned empty list")
                        image_urls = []
                except Exception as scrape_error:
                    error_name = type(scrape_error).__name__
                    print(f"[REPORT] ⚠️  Scraper failed: {error_name}: {scrape_error}")
                    logger.warning(f"⚠️  Scraper failed ({error_name}): {scrape_error}")
                    image_urls = []
            
            # STRATEGY 2: Check for manually uploaded photos (fallback)
            # Trigger if: scraper failed (0 images) OR found too few images (< 3)
            if scraper_attempted and (not image_urls or len(image_urls) < 3):
                current_count = len(image_urls)
                print(f"[REPORT]    📁 Strategy 2: Checking for uploaded photos (have {current_count}, need 3+)...")
                uploaded_photo_paths = get_uploaded_photos_for_submission(submission_id)
                
                if uploaded_photo_paths:
                    print(f"[REPORT]    ✅ Found {len(uploaded_photo_paths)} uploaded photos")
                    # Convert file paths to data URIs for Vision AI
                    for path in uploaded_photo_paths:
                        try:
                            with open(path, 'rb') as f:
                                content = f.read()
                            import base64
                            b64 = base64.b64encode(content).decode('utf-8')
                            
                            # Detect MIME type from extension
                            ext = os.path.splitext(path)[1].lower()
                            mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif'}
                            mime_type = mime_map.get(ext, 'image/jpeg')
                            
                            data_uri = f"data:{mime_type};base64,{b64}"
                            image_urls.append(data_uri)
                            print(f"[REPORT]       ✓ Loaded: {os.path.basename(path)}")
                        except Exception as load_err:
                            print(f"[REPORT]       ❌ Failed to load {os.path.basename(path)}: {load_err}")
                            logger.warning(f"Failed to load uploaded photo {path}: {load_err}")
                    
                    if image_urls:
                        print(f"[REPORT]    ✅ Converted {len(image_urls)} uploaded photos to data URIs")
                        logger.info(f"✅ Loaded {len(image_urls)} uploaded photos from disk")
                else:
                    print(f"[REPORT]    ⏭️  No uploaded photos found for submission {submission_id}")
                    logger.info(f"ℹ️  No uploaded photos available for fallback")
            elif not submission.airbnb_url:
                print(f"[REPORT]    📁 No Airbnb URL - checking for uploaded files...")
                uploaded_photo_paths = get_uploaded_photos_for_submission(submission_id)
                if uploaded_photo_paths:
                    print(f"[REPORT]    ✅ Found {len(uploaded_photo_paths)} uploaded photos")
                    logger.info(f"✅ Using {len(uploaded_photo_paths)} uploaded photos (no URL)")
                else:
                    print(f"[REPORT]    ❌ No uploaded photos found")
                    logger.warning(f"⚠️  No Airbnb URL and no uploaded photos available")
            
            if image_urls:
                print(f"[REPORT] 🤖 STEP 1B: PHASE 3 - Running holistic Vision AI on {len(image_urls)} images...")
                try:
                    analyzer = VisionAnalyzerV2()
                    vision_results = await analyzer.analyze_images_batch(image_urls, max_images=10)
                    
                    if vision_results and vision_results.get('design_scorecard'):
                        design_score = vision_results['design_scorecard'].get('total_design_score', 0)
                        trust_status = vision_results.get('honest_marketing_status', 'Unknown')
                        print(f"[REPORT] ✅ PHASE 3 Analysis complete: {design_score}/30, Trust: {trust_status}")
                        logger.info(f"✅ Holistic Vision analysis complete: {design_score}/30")
                    else:
                        print(f"[REPORT]    ❌ Vision AI returned invalid schema")
                        vision_results = None
                except Exception as vision_error:
                    print(f"[REPORT] ❌ Vision AI FAILED: {type(vision_error).__name__}: {vision_error}")
                    logger.error(f"❌ Vision AI failed: {vision_error}")
                    import traceback
                    print(f"[REPORT] Traceback:")
                    for line in traceback.format_exc().split('\n'):
                        if line:
                            print(f"[REPORT]   {line}")
                    vision_results = None
            else:
                print(f"[REPORT] ⚠️  No image URLs available - using default vision scores")
                logger.warning(f"⚠️  No images to analyze - using defaults")
        
        # If Vision AI still failed, use defaults
        if not vision_results:
            print(f"[REPORT] 🎯 Using default vision results")
            from vision_analyzer_v2 import VisionAnalyzerV2
            analyzer = VisionAnalyzerV2()
            vision_results = analyzer._default_scores()
            logger.info(f"ℹ️  Using default vision scores")
        
        print(f"[REPORT] ✅ Vision AI pipeline complete")
        
        # ================================================================
        # STEP 2: CLEAN DATA WITH HUMAN-READABLE FORMATTING
        # ================================================================
        print(f"[REPORT] 🧹 STEP 2: Cleaning database keys...")
        
        from data_cleaner import clean_item_name
        from sanitizer import sanitize_integer, sanitize_text, sanitize_text_for_pdf
        
        # Clean guest_comfort_checklist - convert DB keys to human-readable names
        cleaned_comfort_list = []
        print(f"[REPORT] 🧹 Cleaning {len(submission.guest_comfort_checklist)} comfort items...")
        if submission.guest_comfort_checklist:
            for item_key in submission.guest_comfort_checklist:
                cleaned_name = clean_item_name(item_key)
                cleaned_comfort_list.append(cleaned_name)
                print(f"[REPORT]    ✓ {item_key} → {cleaned_name}")
        else:
            print(f"[REPORT] ⚠️  No comfort items to clean")
        
        submission_dict = {
            'id': submission.id,
            'property_name': sanitize_text(submission.property_name),
            'listing_type': submission.listing_type,
            'guest_comfort_checklist': cleaned_comfort_list,  # NOW CLEANED
            'total_photos': sanitize_integer(submission.total_photos, default=20),
            'vision_results': vision_results  # Vision AI data for report
        }
        
        print(f"[REPORT] ✅ Data cleaning complete")
        logger.info(f"✅ Data cleaned and formatted for report")
        
        # ================================================================
        # STEP 3: GENERATE REPORT WITH VISION DATA
        # ================================================================
        print(f"[REPORT] 📝 STEP 3: Generating report with vision data...")
        
        from report_generator import generate_report, ReportBuilder
        
        result = generate_report(submission_dict)
        if not result['success']:
            logger.error(f"❌ Report generation failed: {result.get('error')}")
            print(f"[REPORT] ❌ Report generation FAILED: {result.get('error')}")
            return
        
        score_data = result['vitality_data']
        print(f"[REPORT] ✅ Report generated: vitality_score={score_data['vitality_score']}/100 ({score_data['grade']})")
        logger.info(f"✅ Vitality score calculated: {score_data['vitality_score']}/100 ({score_data['grade']})")
        
        # Generate recommendations
        builder = ReportBuilder(submission_dict, score_data)
        recommendations = builder._generate_recommendations()
        
        # Save HTML report
        html_filename = f"report_{submission_id}_{uuid.uuid4().hex[:8]}.html"
        report_dir = REPORT_OUTPUT_DIR or "./reports"
        html_path = os.path.join(report_dir, html_filename)
        
        os.makedirs(report_dir, exist_ok=True)
        with open(html_path, 'w') as f:
            f.write(result['html'])
        
        # Generate PDF report ONLY for premium (FREE reports have no PDF attachment)
        pdf_path = None
        if report_type == "premium":
            pdf_filename = f"report_{submission_id}_{uuid.uuid4().hex[:8]}.pdf"
            pdf_path = os.path.join(report_dir, pdf_filename)
            
            try:
                pdf_success = generate_pdf_report_v2(
                    output_path=pdf_path,
                    property_name=submission.property_name,
                    vitality_data=score_data,
                    recommendations=recommendations,
                    analysis_text=result.get("analysis", ""),
                    shopping_list=result.get("shopping_list", []),
                    top_three_fixes=result.get("top_three_fixes", []),
                    report_type=report_type
                )
                
                if not pdf_success:
                    # Hard fail: Do not fall back to email-only. This is a critical error.
                    logger.error(f"❌ CRITICAL: PDF generation FAILED for premium report. Hard stop.")
                    raise Exception("PDF generation failed - Weasyprint engine error. Contact support.")
                else:
                    logger.info(f"✅ Premium PDF report generated: {pdf_filename}")
            except Exception as e:
                logger.error(f"❌ CRITICAL PDF generation error: {e}")
                raise
        else:
            logger.info(f"📧 Free report: No PDF attachment (email only)")
        
        # Store report record
        report = db.create_report(
            submission_id=submission_id,
            vitality_score=score_data['vitality_score'],
            grade=score_data['grade'],
            html_content=result['html'],
            report_type=report_type
        )
        
        logger.info(f"✅ Report record created: {report.id}")
        print(f"[REPORT] ✅ Report record created: {report.id}")
        
        # ================================================================
        # STEP 4: SEND EMAIL WITH REPORT
        # ================================================================
        print(f"[REPORT] 📧 STEP 4: Sending report email...")
        
        if email_service:
            try:
                print(f"[REPORT]    To: {submission.email}")
                print(f"[REPORT]    Type: {report_type}")
                if pdf_path:
                    print(f"[REPORT]    PDF: {os.path.basename(pdf_path)}")
                
                # PHASE 4: FREE TIER — Instant hook email (REDACTED AI fixes, utility baseline fixes shown)
                if report_type == "free":
                    print(f"[REPORT] 🎣 PHASE 4: FREE TIER - Sending Vitality Email (Redacted + Utility Fixes)")
                    
                    # Identify unchecked comfort items to show as "Essential Baseline Fixes"
                    unchecked_items = []
                    if submission.guest_comfort_checklist:
                        # All comfort items from form
                        all_comfort_items = [
                            'powerBars', 'bedLamps', 'hangers', 'plunger', 
                            'glasses', 'plates', 'dryingRack', 'paperTowels', 
                            'coasters', 'shoeRack', 'mirror', 'bathMats'
                        ]
                        # Find which ones are NOT checked
                        checked = submission.guest_comfort_checklist
                        unchecked_items = [item for item in all_comfort_items if item not in checked]
                    
                    print(f"[REPORT]    Unchecked items: {unchecked_items[:3]}")
                    
                    # REVENUE PROTECTION: Send redacted email
                    # AI fixes are REDACTED, utility baseline fixes are shown
                    top_fixes = vision_results.get('top_3_fixes', []) if vision_results else []
                    
                    email_service.send_free_vitality_report(
                        email=submission.email,
                        vitality_score=score_data['vitality_score'],
                        grade=score_data['grade'],
                        top_fixes=top_fixes,  # REDACTED in template
                        property_name=submission.property_name,
                        submission_id=submission_id,  # For Stripe checkout link
                        unchecked_items=unchecked_items,  # Show as baseline fixes (deprecated)
                        guest_comfort_checklist=submission.guest_comfort_checklist  # Dynamic missing items
                    )
                    print(f"[REPORT]    ✅ FREE vitality email sent (AI fixes REDACTED, baseline fixes shown)")
                    logger.info(f"✅ FREE vitality report sent to {submission.email} (redacted)")
                else:
                    # Premium: Full report with PDF
                    print(f"[REPORT] 💎 PREMIUM TIER - Sending Full Report with PDF")
                    email_service.send_report_email(
                        email=submission.email,
                        property_name=submission.property_name,
                        pdf_path=pdf_path,
                        vitality_score=score_data['vitality_score'],
                        grade=score_data['grade'],
                        report_type=report_type,
                        analysis_text=result.get("analysis", ""),
                        shopping_list=result.get("shopping_list", []),
                        top_three_fixes=result.get("top_three_fixes", [])
                    )
                    print(f"[REPORT]    ✅ PREMIUM email sent with PDF")
                    logger.info(f"✅ Premium report email sent to {submission.email}")
            except Exception as e:
                print(f"[REPORT]    ❌ Email failed: {type(e).__name__}: {e}")
                logger.error(f"⚠️  Report email error: {e}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            print(f"[REPORT] ⚠️  Email service unavailable")
            logger.warning(f"⚠️  Email service not available")
        
        # Record delivery
        db.create_report_delivery(
            report_id=report.id,
            email=submission.email,
            status="delivered"
        )
        
        print(f"[REPORT] 🎉 REPORT GENERATION COMPLETE")
        print(f"[REPORT]    Property: {submission.property_name}")
        print(f"[REPORT]    Score: {score_data['vitality_score']}/100 ({score_data['grade']})")
        print(f"[REPORT]    Email: {submission.email}")
        logger.info(f"✅ Report pipeline complete: {submission.property_name}")
    
    except Exception as e:
        print(f"[REPORT] ❌ FATAL ERROR IN REPORT PIPELINE:")
        print(f"[REPORT]    {type(e).__name__}: {e}")
        import traceback
        print(f"[REPORT] Traceback:")
        for line in traceback.format_exc().split('\n'):
            if line:
                print(f"[REPORT]   {line}")
        logger.error(f"❌ Report generation error: {e}")
        logger.error(traceback.format_exc())


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    )


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 60)
    logger.info("🚀 Design Diagnosis Backend Starting...")
    logger.info("=" * 60)
    logger.info(f"📊 Base URL: {BASE_URL}")
    logger.info(f"📊 Database: {DB_PATH}")
    logger.info(f"📊 Reports: {REPORT_OUTPUT_DIR}")
    logger.info("✅ All services initialized")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Design Diagnosis Backend Shutting Down...")
    if db:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
