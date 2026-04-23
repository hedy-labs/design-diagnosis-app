"""
Design Diagnosis Data Models

Pydantic models for request/response validation
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


# ============================================================================
# FORM SUBMISSION MODELS
# ============================================================================

class FormSubmitInput(BaseModel):
    """Form submission input from user"""
    email: str
    property_name: str
    airbnb_url: Optional[str] = None
    listing_type: str
    bedrooms: int
    bathrooms: int
    guest_capacity: int
    total_photos: str
    guest_comfort_checklist: List[str]
    report_type: str  # "free" or "premium"
    wants_marketing_emails: bool = False  # Opt-in for marketing emails
    
    @validator('report_type')
    def validate_report_type(cls, v):
        if v not in ['free', 'premium']:
            raise ValueError("report_type must be 'free' or 'premium'")
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError("Invalid email address")
        return v


class FormSubmitResponse(BaseModel):
    """Response after form submission"""
    success: bool
    message: str
    submission_id: Optional[int] = None
    next_step: str


# ============================================================================
# EMAIL VERIFICATION MODELS
# ============================================================================

class EmailVerificationInput(BaseModel):
    """Email verification with token"""
    token: str


class EmailVerificationResponse(BaseModel):
    """Response after email verification"""
    success: bool
    message: str
    report_url: Optional[str] = None


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class CreatePaymentInput(BaseModel):
    """Request to create Stripe payment intent"""
    submission_id: int
    property_name: str
    return_url: Optional[str] = None


class CreatePaymentResponse(BaseModel):
    """Response with payment intent details"""
    success: bool
    client_secret: Optional[str] = None
    message: str


class PaymentWebhookInput(BaseModel):
    """Stripe webhook event"""
    type: str
    data: dict


# ============================================================================
# REPORT MODELS
# ============================================================================

class ReportResponse(BaseModel):
    """Report retrieval response"""
    success: bool
    report_id: int
    property_name: str
    vitality_score: Optional[float] = None
    grade: Optional[str] = None
    file_url: Optional[str] = None


# ============================================================================
# HEALTH CHECK MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    services: dict
