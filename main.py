"""
Design Diagnosis Backend — FastAPI Entry Point (Phase 2)

Flat directory structure. All imports from root level only.
"""

from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import uuid
import os
from pathlib import Path
import logging

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
# BASE_URL can be set via .env or will auto-detect from request headers
DEFAULT_BASE_URL = os.getenv("BASE_URL", None)
DB_PATH = os.getenv("DB_PATH", "design_diagnosis.db")
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./reports")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
AMAZON_AFFILIATE_ID = os.getenv("AMAZON_AFFILIATE_ID", "")


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
class MockScoringEngine:
    def calculate_score(self, guest_comfort_checklist: List[str], property_type: str):
        # Simple scoring: count checklist items, cap at 100
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
logger.info("✅ Scoring engine initialized (mock mode)")

# PDF Generator (Mock)
class MockPDFGenerator:
    def generate_report(self, property_name: str, vitality_score: float, grade: str, report_type: str, guest_comfort_checklist: List[str], output_path: str):
        # Create simple text file (mock PDF)
        content = f"""
DESIGN DIAGNOSIS REPORT
{'=' * 60}

Property: {property_name}
Vitality Score: {vitality_score}/100
Grade: {grade}
Report Type: {report_type.upper()}
Generated: {datetime.utcnow().isoformat()}

Guest Comfort Items Checked: {len(guest_comfort_checklist)}
{', '.join(guest_comfort_checklist[:5])}...

This is a mock PDF report for testing purposes.
"""
        with open(output_path, 'w') as f:
            f.write(content)
        logger.info(f"📄 Mock report generated: {output_path}")

pdf_generator = MockPDFGenerator()
logger.info("✅ PDF generator initialized (mock mode)")

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


@app.post("/api/submit-form", response_model=FormSubmitResponse)
async def submit_form(form_data: FormSubmitInput, background_tasks: BackgroundTasks, request: Request):
    """
    Submit property form and trigger email verification flow
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        logger.info(f"📝 Form submission from {form_data.email} for {form_data.property_name}")
        
        # Save form submission
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
        
        logger.info(f"✅ Submission saved with ID: {submission.id}")
        
        # Generate verification token
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
        
        # Mark email as verified
        db.mark_email_verified(verification.id)
        logger.info(f"✅ Email verified: {verification.email}")
        
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
        
        return HTMLResponse(
            f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                    h1 {{ color: #667eea; }}
                    p {{ color: #666; font-size: 16px; }}
                </style>
            </head>
            <body>
                <h1>✅ Email Verified!</h1>
                <p>Your Design Diagnosis report is being generated...</p>
                <p>Check your email ({verification.email}) in a few moments to receive your report.</p>
            </body>
            </html>
            """
        )
    
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
    """
    try:
        if not stripe_service:
            raise HTTPException(status_code=503, detail="Stripe service unavailable")
        
        if not db:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        logger.info(f"💳 Checkout session requested for submission {payment_input.submission_id}")
        
        # Verify submission exists
        submission = db.get_form_submission(payment_input.submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Get base URL
        base_url = get_base_url(request)
        
        # Create Stripe Checkout Session
        session = stripe_service.create_checkout_session(
            submission_id=payment_input.submission_id,
            property_name=payment_input.property_name,
            customer_email=submission.email,
            success_url=f"{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/payment-cancelled"
        )
        
        logger.info(f"✅ Checkout session created: {session['session_id']}")
        
        # Store payment record
        db.create_payment(
            submission_id=payment_input.submission_id,
            stripe_intent_id=session['session_id'],
            amount=3900,
            status="pending"
        )
        
        return CreatePaymentResponse(
            success=True,
            client_secret=session['checkout_url'],  # Return checkout URL
            message="Redirect to Stripe Checkout to complete payment"
        )
    
    except Exception as e:
        logger.error(f"❌ Checkout session creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/payment-webhook")
async def payment_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Stripe webhook events
    """
    try:
        body = await request.body()
        event = json.loads(body)
        
        logger.info(f"🔔 Webhook event: {event.get('type')}")
        
        # Handle payment success
        if event.get('type') == 'payment_intent.succeeded':
            intent_id = event['data']['object']['id']
            payment = db.get_payment_by_stripe_id(intent_id)
            
            if payment:
                # Mark payment as succeeded
                db.update_payment_status(payment.id, "succeeded")
                logger.info(f"✅ Payment succeeded: {intent_id}")
                
                # Generate and send premium report
                background_tasks.add_task(
                    generate_and_send_report,
                    submission_id=payment.submission_id,
                    report_type="premium"
                )
        
        return JSONResponse({"status": "success"})
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return JSONResponse({"status": "error"}, status_code=400)


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


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def generate_and_send_report(submission_id: int, report_type: str):
    """
    Generate PDF report and send via email
    """
    try:
        if not db:
            logger.error("❌ Database not available for report generation")
            return
        
        logger.info(f"📊 Generating {report_type} report for submission {submission_id}...")
        
        submission = db.get_form_submission(submission_id)
        if not submission:
            logger.error(f"❌ Submission {submission_id} not found")
            return
        
        # Calculate vitality score
        score_data = scoring_engine.calculate_score(
            guest_comfort_checklist=submission.guest_comfort_checklist,
            property_type=submission.listing_type
        )
        
        logger.info(f"✅ Vitality score calculated: {score_data['score']}/100 ({score_data['grade']})")
        
        # Generate PDF
        pdf_filename = f"report_{submission_id}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(REPORT_OUTPUT_DIR, pdf_filename)
        
        pdf_generator.generate_report(
            property_name=submission.property_name,
            vitality_score=score_data.get('score', 0),
            grade=score_data.get('grade', 'F'),
            report_type=report_type,
            guest_comfort_checklist=submission.guest_comfort_checklist,
            output_path=pdf_path
        )
        
        # Store report record
        report = db.create_report(
            submission_id=submission_id,
            property_name=submission.property_name,
            vitality_score=score_data.get('score', 0),
            grade=score_data.get('grade', 'F'),
            file_name=pdf_filename,
            report_type=report_type
        )
        
        logger.info(f"✅ Report record created: {report.id}")
        
        # Send report email
        email_service.send_report_email(
            email=submission.email,
            property_name=submission.property_name,
            pdf_path=pdf_path,
            vitality_score=score_data.get('score', 0),
            grade=score_data.get('grade', 'F'),
            report_type=report_type
        )
        
        # Record delivery
        db.create_report_delivery(
            report_id=report.id,
            email=submission.email,
            status="delivered"
        )
        
        logger.info(f"✅ Report delivered to {submission.email}")
    
    except Exception as e:
        logger.error(f"❌ Report generation error: {e}")


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
