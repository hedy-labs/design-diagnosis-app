"""
Stripe Payment Service

Handles Stripe Checkout Sessions and webhooks
"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import Stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  stripe package not installed. Payments will use mock mode.")
    STRIPE_AVAILABLE = False


class StripeService:
    """Stripe payment service with Checkout Sessions"""
    
    def __init__(self):
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        
        if self.secret_key and STRIPE_AVAILABLE:
            try:
                stripe.api_key = self.secret_key
                self.mode = "LIVE"
                logger.info("✅ Stripe initialized (LIVE mode)")
            except Exception as e:
                logger.error(f"❌ Stripe initialization failed: {e}")
                self.mode = "MOCK"
        else:
            self.mode = "MOCK"
            if not self.secret_key:
                logger.warning("⚠️  STRIPE_SECRET_KEY not set. Using mock payment mode.")
            if not STRIPE_AVAILABLE:
                logger.warning("⚠️  stripe package not installed. Using mock payment mode.")
    
    def create_checkout_session(
        self,
        submission_id: int,
        property_name: str,
        customer_email: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """
        Create a Stripe Checkout Session for premium report payment
        
        Returns: {
            'session_id': 'cs_...',
            'checkout_url': 'https://checkout.stripe.com/...',
            'mode': 'LIVE' or 'MOCK'
        }
        """
        try:
            if self.mode == "LIVE" and STRIPE_AVAILABLE:
                return self._create_live_session(
                    submission_id=submission_id,
                    property_name=property_name,
                    customer_email=customer_email,
                    success_url=success_url,
                    cancel_url=cancel_url
                )
            else:
                return self._create_mock_session(
                    submission_id=submission_id,
                    property_name=property_name
                )
        
        except Exception as e:
            logger.error(f"❌ Checkout session creation error: {e}")
            raise
    
    def _create_live_session(
        self,
        submission_id: int,
        property_name: str,
        customer_email: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """Create live Stripe Checkout Session"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Design Diagnosis Premium Report",
                                "description": f"Complete design analysis for: {property_name}",
                                "images": [],  # Optional: add logo URL here
                            },
                            "unit_amount": 3900,  # $39.00 in cents
                        },
                        "quantity": 1,
                    }
                ],
                customer_email=customer_email,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "submission_id": str(submission_id),
                    "property_name": property_name,
                },
            )
            
            logger.info(f"✅ Checkout session created: {session.id}")
            
            return {
                "session_id": session.id,
                "checkout_url": session.url,
                "mode": "LIVE"
            }
        
        except Exception as e:
            logger.error(f"❌ Live checkout error: {e}")
            raise
    
    def _create_mock_session(
        self,
        submission_id: int,
        property_name: str
    ) -> Dict:
        """Create mock Stripe session (for testing without API key)"""
        logger.info(f"📋 [MOCK] Checkout session for submission {submission_id}")
        
        return {
            "session_id": f"cs_mock_{submission_id}",
            "checkout_url": f"https://stripe-mock.example.com/checkout?session_id=cs_mock_{submission_id}",
            "mode": "MOCK"
        }
    
    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """
        Verify and parse Stripe webhook signature
        
        Returns: parsed event dict or None if invalid
        """
        if self.mode == "MOCK":
            logger.info("📋 [MOCK] Webhook verification skipped (mock mode)")
            return None
        
        if not STRIPE_AVAILABLE:
            return None
        
        try:
            webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
            if not webhook_secret:
                logger.warning("⚠️  STRIPE_WEBHOOK_SECRET not set. Webhook verification skipped.")
                return None
            
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                webhook_secret
            )
            
            logger.info(f"✅ Webhook verified: {event['type']}")
            return event
        
        except Exception as e:
            logger.error(f"❌ Webhook verification error: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve Stripe session details"""
        if self.mode == "MOCK":
            logger.info(f"📋 [MOCK] Retrieved session {session_id}")
            return {"id": session_id, "payment_status": "paid"}
        
        if not STRIPE_AVAILABLE:
            return None
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except Exception as e:
            logger.error(f"❌ Session retrieval error: {e}")
            return None
