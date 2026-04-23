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
# BASE_URL: explicit fallback for VPS/production
BASE_URL = "http://147.182.247.168:8000"  # Default VPS IP

# Override with .env if set
DEFAULT_BASE_URL = os.getenv("BASE_URL", BASE_URL)
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
# Import real PDF generator (not mock)
try:
    from pdf_generator import generate_pdf_report, generate_html_as_pdf_fallback
    pdf_available = True
    logger.info("✅ PDF generator initialized (real mode with fpdf2)")
except ImportError:
    logger.warning("⚠️  fpdf2 not available, PDF generation will use HTML fallback")
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


@app.post("/api/submit-form", response_model=FormSubmitResponse)
async def submit_form(form_data: FormSubmitInput, background_tasks: BackgroundTasks, request: Request):
    """
    Submit property form with zero-friction for returning verified users
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        logger.info(f"📝 Form submission from {form_data.email} for {form_data.property_name}")
        
        # Validate: Airbnb URL is required
        if not form_data.airbnb_url or not form_data.airbnb_url.strip():
            raise HTTPException(
                status_code=400,
                detail="Airbnb/VRBO URL is required. Please provide your listing URL."
            )
        
        # Validate: URL contains airbnb or vrbo
        url_lower = form_data.airbnb_url.lower()
        if 'airbnb' not in url_lower and 'vrbo' not in url_lower:
            raise HTTPException(
                status_code=400,
                detail="Please enter a valid Airbnb or VRBO listing URL."
            )
        
        # Check if user is already verified (zero-friction return)
        user = db.get_or_create_user(form_data.email)
        is_returning_verified = user.is_verified
        
        logger.info(f"🔍 User status: {'Returning Verified ✅' if is_returning_verified else 'New/Unverified'}")
        
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
            cancel_url=f"{base_url}/payment-cancelled?session_id={{CHECKOUT_SESSION_ID}}"
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
            
            logger.info(f"💳 Checkout session completed: {session_id}")
            
            if not db:
                logger.error("❌ Database unavailable for webhook")
                return JSONResponse({"error": "DB unavailable"}, status_code=503)
            
            # Get payment
            payment = db.get_payment_by_stripe_id(session_id)
            if not payment:
                logger.error(f"❌ Payment not found for session {session_id}")
                return JSONResponse({"error": "Payment not found"}, status_code=404)
            
            # Mark payment as completed
            db.update_payment_status(payment.id, "completed")
            logger.info(f"✅ Payment marked completed: {payment.id}")
            
            # Get submission
            submission = db.get_form_submission(payment.submission_id)
            if not submission:
                logger.error(f"❌ Submission not found for payment {payment.id}")
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
async def payment_success():
    """Serve the payment success page"""
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
        
        # Generate vitality score using real report generator
        from report_generator import generate_report, ReportBuilder
        from pdf_generator import generate_pdf_report
        
        # Sanitize all form data
        from sanitizer import sanitize_integer, sanitize_text, sanitize_text_for_pdf
        
        submission_dict = {
            'id': submission.id,
            'property_name': sanitize_text(submission.property_name),
            'listing_type': submission.listing_type,
            'guest_comfort_checklist': submission.guest_comfort_checklist,
            'total_photos': sanitize_integer(submission.total_photos, default=20),
        }
        
        result = generate_report(submission_dict)
        if not result['success']:
            logger.error(f"❌ Report generation failed: {result.get('error')}")
            return
        
        score_data = result['vitality_data']
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
        
        # Generate PDF report (if fpdf2 available, otherwise HTML fallback)
        pdf_filename = html_filename.replace('.html', '.pdf')
        pdf_path = os.path.join(report_dir, pdf_filename)
        
        pdf_success = generate_pdf_report(
            output_path=pdf_path,
            property_name=submission.property_name,
            vitality_data=score_data,
            recommendations=recommendations
        )
        
        if not pdf_success:
            # Fallback to HTML
            from pdf_generator import generate_html_as_pdf_fallback
            generate_html_as_pdf_fallback(pdf_path, result['html'])
            logger.info(f"📄 Using HTML fallback for report")
        
        # Store report record
        report = db.create_report(
            submission_id=submission_id,
            vitality_score=score_data['vitality_score'],
            grade=score_data['grade'],
            html_content=result['html'],
            report_type=report_type
        )
        
        logger.info(f"✅ Report record created: {report.id}")
        
        # Send report email
        if email_service:
            try:
                email_service.send_report_email(
                    email=submission.email,
                    property_name=submission.property_name,
                    pdf_path=pdf_path,
                    vitality_score=score_data['vitality_score'],
                    grade=score_data['grade'],
                    report_type=report_type
                )
                logger.info(f"✅ Report email sent to {submission.email}")
            except Exception as e:
                logger.error(f"⚠️  Report email error: {e}")
        
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
