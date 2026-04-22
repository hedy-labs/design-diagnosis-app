"""
Design Diagnosis Backend — FastAPI Server (Phase 2)

Core API endpoints:
- POST /api/submit-form — Form submission with property data + guest comfort checklist + email
- POST /api/verify-email — Email verification endpoint (token validation)
- POST /api/create-payment — Create Stripe payment intent for premium reports
- POST /api/payment-webhook — Stripe webhook for payment completion
- GET /api/report/{report_id} — Retrieve completed report
- GET /health — Health check

Phase 2 Features:
✓ Email collection (required for report)
✓ Email verification (token-based)
✓ Free vs Premium reports
✓ Stripe sandbox payment flow
✓ PDF generation & delivery
✓ Affiliate shopping links
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import json
import uuid
import os
from pathlib import Path

from database import (
    DesignDiagnosisDB, Property, Report, FormSubmission, EmailVerification,
    Payment, ReportDelivery
)
from email_service import EmailService
from stripe_service import StripeService
from scoring import ScoringEngine, ScoringInput, PhotoStrategyScorer, HiddenFrictionScorer
from pdf_report import VitalityReportPDF


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
REPORT_OUTPUT_DIR = "./design-diagnosis-app/reports"
Path(REPORT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Services
db = DesignDiagnosisDB(os.getenv("DB_PATH", "design_diagnosis.db"))
email_service = EmailService()
stripe_service = StripeService()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FormSubmitInput(BaseModel):
    """Form submission input"""
    email: str  # EmailStr would validate but we'll be lenient here
    property_name: str
    airbnb_url: Optional[str] = None
    listing_type: str  # House, Condo, Apartment, etc.
    bedrooms: int
    bathrooms: int
    guest_capacity: int
    total_photos: str  # "0-5", "6-10", etc.
    guest_comfort_checklist: List[str]  # List of checked item names
    report_type: str  # "free" or "premium"
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "host@example.com",
                "property_name": "Beachside Bungalow",
                "airbnb_url": "https://www.airbnb.com/rooms/12345",
                "listing_type": "House",
                "bedrooms": 3,
                "bathrooms": 2,
                "guest_capacity": 6,
                "total_photos": "15-20",
                "guest_comfort_checklist": ["wifi", "linens", "welcome_basket"],
                "report_type": "premium"
            }
        }


class EmailVerificationInput(BaseModel):
    """Email verification confirmation"""
    token: str


class CreatePaymentInput(BaseModel):
    """Request to create payment intent"""
    submission_id: int
    property_name: str
    return_url: Optional[str] = None


class WebhookPayload(BaseModel):
    """Generic webhook payload (will be validated against Stripe signature)"""
    pass


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Design Diagnosis Backend — Phase 2",
    description="Email verification, PDF generation, Stripe payment, affiliate shopping",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_verification_token() -> str:
    """Generate unique verification token"""
    return str(uuid.uuid4())


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    return request.client.host if request.client else "unknown"


def calculate_vitality_score_from_submission(submission: FormSubmission) -> Tuple[float, str, float]:
    """
    Calculate vitality score from form submission
    (In real scenario, this would analyze uploaded photos)
    """
    # Parse checklist
    try:
        checklist_items = json.loads(submission.guest_comfort_checklist) if isinstance(
            submission.guest_comfort_checklist, str
        ) else submission.guest_comfort_checklist
    except:
        checklist_items = []
    
    # Simplified scoring based on property details + checklist
    # In production, this would use Claude Vision on actual photos
    
    base_score = 50  # Start with base
    
    # Property size factor
    if submission.bedrooms >= 3 and submission.bathrooms >= 2:
        base_score += 10
    
    # Guest capacity alignment
    if submission.guest_capacity <= (submission.bedrooms * 2):
        base_score += 5
    
    # Checklist items present
    base_score += len(checklist_items) * 2
    
    # Photo coverage
    photo_ranges = {
        "0-5": 5, "6-10": 10, "11-15": 15, "16-20": 18,
        "21-30": 20, "31-40": 20, "41-50": 20, "51+": 20
    }
    photo_score = photo_ranges.get(submission.total_photos, 10)
    base_score += photo_score
    
    # Cap at 100
    vitality_score = min(100, base_score)
    
    # Grade
    if vitality_score >= 90:
        grade = "A"
    elif vitality_score >= 80:
        grade = "B"
    elif vitality_score >= 70:
        grade = "C"
    elif vitality_score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    # Total points (scale to 150-point system)
    total_points = (vitality_score / 100) * 150
    
    return vitality_score, grade, total_points


def generate_pdf_report(
    submission: FormSubmission, vitality_score: float, grade: str,
    report_type: str = "free"
) -> Optional[str]:
    """
    Generate PDF report and save to disk
    Returns: path to saved PDF
    """
    try:
        filename = f"{submission.property_name.replace(' ', '_')}_{submission.id}_{report_type}.pdf"
        output_path = os.path.join(REPORT_OUTPUT_DIR, filename)
        
        # Create PDF generator
        pdf_gen = VitalityReportPDF(output_path)
        
        # Parse checklist
        try:
            checklist_items = json.loads(submission.guest_comfort_checklist) if isinstance(
                submission.guest_comfort_checklist, str
            ) else submission.guest_comfort_checklist
        except:
            checklist_items = []
        
        # Build report data
        report_data = {
            "property_name": submission.property_name,
            "listing_type": submission.listing_type,
            "bedrooms": submission.bedrooms,
            "bathrooms": submission.bathrooms,
            "guest_capacity": submission.guest_capacity,
            "vitality_score": vitality_score,
            "grade": grade,
            "checklist_items": checklist_items,
            "report_type": report_type
        }
        
        # Generate PDF (uses ReportLab)
        pdf_gen.generate_report(report_data)
        
        print(f"✅ PDF generated: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return None


# ============================================================================
# ENDPOINTS — PHASE 1 (EXISTING)
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "2",
        "services": {
            "email": "configured" if email_service.is_configured() else "mock",
            "stripe": "test" if stripe_service.is_test_mode else "mock"
        }
    }


# ============================================================================
# ENDPOINTS — PHASE 2 (NEW)
# ============================================================================

@app.post("/api/submit-form")
async def submit_form(input_data: FormSubmitInput, request: Request):
    """
    Submit property form with guest comfort checklist and email
    
    Returns: submission ID, status, and instructions
    """
    try:
        # Validate email format (basic)
        if not input_data.email or "@" not in input_data.email:
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Create form submission
        submission = FormSubmission(
            email=input_data.email,
            property_name=input_data.property_name,
            airbnb_url=input_data.airbnb_url or "",
            listing_type=input_data.listing_type,
            bedrooms=input_data.bedrooms,
            bathrooms=input_data.bathrooms,
            guest_capacity=input_data.guest_capacity,
            total_photos=input_data.total_photos,
            guest_comfort_checklist=json.dumps(input_data.guest_comfort_checklist),
            report_type=input_data.report_type,
            ip_address=get_client_ip(request)
        )
        
        submission_id = db.create_form_submission(submission)
        
        # Generate verification token
        token = generate_verification_token()
        token_expiry = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        db.create_email_verification(submission_id, input_data.email, token, token_expiry)
        
        # Build verification link
        verification_link = f"{BASE_URL}/api/verify-email?token={token}"
        
        # Send verification email
        email_sent = email_service.send_verification_email(
            input_data.email, verification_link, input_data.property_name
        )
        
        return {
            "success": True,
            "submission_id": submission_id,
            "email": input_data.email,
            "report_type": input_data.report_type,
            "status": "verification_pending",
            "message": f"Verification email sent to {input_data.email}. Check your inbox.",
            "email_sent": email_sent,
            "next_step": "Verify email address to get your report"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/verify-email")
async def verify_email(token: str, background_tasks: BackgroundTasks):
    """
    Verify email address and trigger report generation
    
    If FREE: Generate and email basic report immediately
    If PREMIUM: Redirect to Stripe payment
    """
    try:
        # Validate token
        verification = db.get_email_verification_by_token(token)
        
        if not verification:
            raise HTTPException(status_code=404, detail="Invalid or expired token")
        
        if verification.verified:
            return {
                "success": False,
                "message": "Email already verified",
                "status": "already_verified"
            }
        
        # Check token expiry
        try:
            expiry_time = datetime.fromisoformat(verification.token_expiry)
            if datetime.utcnow() > expiry_time:
                raise HTTPException(status_code=400, detail="Verification token expired")
        except:
            pass
        
        # Mark email as verified
        db.mark_email_verified(token)
        
        # Get submission details
        submission = db.get_form_submission(verification.submission_id)
        
        if submission.report_type == "free":
            # Generate and send free report immediately
            background_tasks.add_task(
                generate_and_send_free_report,
                verification.submission_id,
                submission
            )
            return {
                "success": True,
                "status": "generating",
                "message": "Your free report is being generated and will be sent shortly",
                "next_step": "Check your email in 2-3 minutes"
            }
        else:  # premium
            # Redirect to payment
            return {
                "success": True,
                "status": "payment_required",
                "submission_id": verification.submission_id,
                "message": "Email verified! Proceeding to payment",
                "next_step": "Complete payment to get your premium report"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/create-payment")
async def create_payment(input_data: CreatePaymentInput):
    """
    Create Stripe payment intent for premium report
    
    Returns: payment intent ID and client secret (for Stripe.js integration)
    """
    try:
        submission = db.get_form_submission(input_data.submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if submission.report_type != "premium":
            raise HTTPException(status_code=400, detail="Submission is not premium")
        
        # Check if email is verified
        verification = db.get_email_verification_by_submission(input_data.submission_id)
        
        if not verification or not verification.verified:
            raise HTTPException(status_code=400, detail="Email not verified")
        
        # Create payment intent via Stripe
        payment_intent_id, success = stripe_service.create_payment_intent(
            amount_cents=stripe_service.PREMIUM_PRICE_CENTS,
            description=f"Design Diagnosis Premium Report - {input_data.property_name}",
            metadata={
                "submission_id": input_data.submission_id,
                "property_name": input_data.property_name,
                "email": submission.email
            }
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create payment intent")
        
        # Store payment record
        payment_id = db.create_payment(
            submission_id=input_data.submission_id,
            stripe_payment_intent_id=payment_intent_id,
            amount=stripe_service.PREMIUM_PRICE_CENTS,
            status="pending",
            report_type="premium"
        )
        
        # Get intent details
        intent_details = stripe_service.get_payment_intent(payment_intent_id)
        
        return {
            "success": True,
            "payment_id": payment_id,
            "payment_intent_id": payment_intent_id,
            "client_secret": intent_details.get("client_secret") if intent_details else None,
            "amount": stripe_service.PREMIUM_PRICE_CENTS,
            "amount_usd": f"${stripe_service.PREMIUM_PRICE_USD}",
            "message": "Payment intent created. Complete payment to generate report.",
            "test_card": stripe_service.test_card_number(),
            "next_step": "Use Stripe.js to complete payment"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payment-webhook")
async def payment_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Stripe webhook handler for payment completion
    
    Triggers PDF generation and email delivery on successful payment
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("stripe-signature", "")
        
        # Verify webhook signature
        is_valid, event = stripe_service.verify_webhook_signature(
            body.decode('utf-8'),
            signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})
        
        # Handle payment intent succeeded
        if event_type == "payment_intent.succeeded":
            payment_intent_id = event_data.get("id")
            metadata = event_data.get("metadata", {})
            
            # Find payment in database
            payment = db.get_payment_by_intent(payment_intent_id)
            
            if not payment:
                print(f"⚠️  Payment intent {payment_intent_id} not found in DB")
                return {"received": True}  # Still return 200 to Stripe
            
            # Mark webhook as received
            db.mark_webhook_received(payment.id)
            
            # Update payment status
            db.update_payment_status(payment.id, "succeeded")
            
            # Get submission details
            submission = db.get_form_submission(payment.submission_id)
            
            # Send payment confirmation email
            email_service.send_payment_confirmation_email(
                submission.email,
                submission.property_name,
                f"${stripe_service.PREMIUM_PRICE_USD}"
            )
            
            # Generate and send premium report in background
            background_tasks.add_task(
                generate_and_send_premium_report,
                payment.submission_id,
                submission
            )
            
            print(f"✅ Payment succeeded: {payment_intent_id}")
        
        # Handle payment intent failed
        elif event_type == "payment_intent.payment_failed":
            payment_intent_id = event_data.get("id")
            payment = db.get_payment_by_intent(payment_intent_id)
            
            if payment:
                db.update_payment_status(payment.id, "failed")
                print(f"❌ Payment failed: {payment_intent_id}")
        
        return {"received": True}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        return {"received": False, "error": str(e)}


@app.get("/api/report/{report_id}")
async def get_report(report_id: int):
    """Retrieve completed report"""
    try:
        report = db.get_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        property_obj = db.get_property(report.property_id)
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return {
            "report_id": report.id,
            "property_id": report.property_id,
            "property_name": property_obj.property_name,
            "vitality_score": report.vitality_score,
            "grade": report.grade,
            "total_points": report.total_points,
            "created_at": report.created_at,
            "pdf_path": report.report_pdf_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def generate_and_send_free_report(submission_id: int, submission: FormSubmission):
    """Background task: Generate free report and send via email"""
    try:
        # Calculate vitality score
        vitality_score, grade, total_points = calculate_vitality_score_from_submission(submission)
        
        # Generate PDF
        pdf_path = generate_pdf_report(submission, vitality_score, grade, "free")
        
        if not pdf_path:
            print(f"❌ Failed to generate PDF for submission {submission_id}")
            return
        
        # Create delivery record
        delivery_id = db.create_report_delivery(
            submission_id, submission.email, "free", pdf_path
        )
        
        # Send email with PDF
        email_sent = email_service.send_report_email(
            submission.email,
            submission.property_name,
            "free",
            pdf_path,
            f"{submission.property_name}_free_report.pdf"
        )
        
        # Mark as sent
        if email_sent:
            db.mark_delivery_sent(delivery_id, "sent")
            print(f"✅ Free report sent to {submission.email}")
        else:
            db.mark_delivery_sent(delivery_id, "failed")
            print(f"❌ Failed to send free report to {submission.email}")
    
    except Exception as e:
        print(f"❌ Background task error (free report): {e}")


async def generate_and_send_premium_report(submission_id: int, submission: FormSubmission):
    """Background task: Generate premium report and send via email"""
    try:
        # Calculate vitality score
        vitality_score, grade, total_points = calculate_vitality_score_from_submission(submission)
        
        # Generate PDF
        pdf_path = generate_pdf_report(submission, vitality_score, grade, "premium")
        
        if not pdf_path:
            print(f"❌ Failed to generate PDF for submission {submission_id}")
            return
        
        # Create delivery record
        delivery_id = db.create_report_delivery(
            submission_id, submission.email, "premium", pdf_path
        )
        
        # Send email with PDF
        email_sent = email_service.send_report_email(
            submission.email,
            submission.property_name,
            "premium",
            pdf_path,
            f"{submission.property_name}_premium_report.pdf"
        )
        
        # Mark as sent
        if email_sent:
            db.mark_delivery_sent(delivery_id, "sent")
            print(f"✅ Premium report sent to {submission.email}")
        else:
            db.mark_delivery_sent(delivery_id, "failed")
            print(f"❌ Failed to send premium report to {submission.email}")
    
    except Exception as e:
        print(f"❌ Background task error (premium report): {e}")


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Design Diagnosis Backend (Phase 2) starting...")
    print(f"   Email Service: {'✅ SendGrid' if email_service.is_configured() else '⚠️  Mock Mode'}")
    print(f"   Stripe: {'✅ Test Mode' if stripe_service.is_test_mode else '⚠️  Mock Mode'}")
    print(f"   Report Output: {REPORT_OUTPUT_DIR}")
    print(f"   Base URL: {BASE_URL}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
