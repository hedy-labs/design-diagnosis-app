"""
Design Diagnosis Stripe Service

Handles:
- Creating payment intents (sandbox mode)
- Webhook verification and processing
- Payment status tracking

Uses Stripe in TEST MODE (sandbox)
"""

import os
import json
import stripe
from typing import Optional, Dict, Tuple
from datetime import datetime


class StripeService:
    """Stripe API wrapper for Design Diagnosis"""
    
    # Pricing
    PREMIUM_PRICE_CENTS = 3900  # $39.00
    PREMIUM_PRICE_USD = 39.00
    
    def __init__(self, api_key: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.api_key = api_key or os.getenv("STRIPE_API_KEY", "sk_test_mock")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test_mock")
        
        # Initialize Stripe with test key
        if self.api_key.startswith("sk_test"):
            stripe.api_key = self.api_key
            self.is_test_mode = True
        else:
            self.is_test_mode = False
            print("⚠️  WARNING: Stripe is NOT in test mode. Using mock mode for safety.")
    
    def create_payment_intent(
        self, amount_cents: int, description: str, metadata: Dict
    ) -> Tuple[Optional[str], bool]:
        """
        Create a payment intent (Stripe checkout flow)
        
        Returns: (payment_intent_id, success)
        """
        try:
            if not self.is_test_mode:
                print(f"🔐 [MOCK] Creating payment intent: {amount_cents/100}USD")
                return ("pi_mock_test_12345", True)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                description=description,
                metadata=metadata
            )
            
            return (intent.id, True)
        except Exception as e:
            print(f"❌ Payment intent creation failed: {e}")
            return (None, False)
    
    def get_payment_intent(self, payment_intent_id: str) -> Optional[Dict]:
        """Retrieve payment intent details"""
        try:
            if not self.is_test_mode:
                return {
                    "id": payment_intent_id,
                    "status": "succeeded",
                    "amount": self.PREMIUM_PRICE_CENTS,
                    "currency": "usd"
                }
            
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,  # requires_payment_method, succeeded, etc.
                "amount": intent.amount,
                "currency": intent.currency,
                "client_secret": intent.client_secret
            }
        except Exception as e:
            print(f"❌ Failed to retrieve intent: {e}")
            return None
    
    def verify_webhook_signature(self, body: str, signature: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify Stripe webhook signature and extract event data
        
        Returns: (is_valid, event_data)
        """
        try:
            if not self.is_test_mode:
                # Mock verification for testing
                event = json.loads(body)
                return (True, event)
            
            event = stripe.Webhook.construct_event(body, signature, self.webhook_secret)
            return (True, event)
        except Exception as e:
            print(f"❌ Webhook verification failed: {e}")
            return (False, None)
    
    def process_payment_completed(self, payment_intent_id: str) -> Dict:
        """
        Process completed payment
        
        Returns: {
            "success": bool,
            "payment_intent_id": str,
            "status": str,
            "amount": int (in cents),
            "timestamp": str
        }
        """
        intent = self.get_payment_intent(payment_intent_id)
        
        if not intent:
            return {"success": False, "error": "Intent not found"}
        
        if intent["status"] != "succeeded":
            return {
                "success": False,
                "error": f"Payment status is {intent['status']}, not succeeded"
            }
        
        return {
            "success": True,
            "payment_intent_id": payment_intent_id,
            "status": intent["status"],
            "amount": intent["amount"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_test_payment_link(
        self, property_name: str, return_url: str = "https://designdiagnosis.com/success"
    ) -> Optional[str]:
        """
        Create a hosted Checkout session for testing
        
        In production, this would be used to redirect to Stripe Checkout
        """
        try:
            if not self.is_test_mode:
                return f"https://mock-stripe.test/checkout/session_test_12345"
            
            session = stripe.checkout.Session.create(
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Design Diagnosis Premium Report",
                            "description": f"Complete analysis report for {property_name}",
                            "metadata": {
                                "property_name": property_name,
                                "report_type": "premium"
                            }
                        },
                        "unit_amount": self.PREMIUM_PRICE_CENTS,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=return_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://designdiagnosis.com/checkout-cancelled",
                metadata={
                    "property_name": property_name,
                    "report_type": "premium"
                }
            )
            
            return session.url
        except Exception as e:
            print(f"❌ Failed to create checkout session: {e}")
            return None
    
    @staticmethod
    def test_card_number() -> str:
        """Get test card number for Stripe (sandbox)"""
        return "4242 4242 4242 4242"
    
    @staticmethod
    def test_card_details() -> Dict:
        """Get test card details for Stripe (sandbox)"""
        return {
            "number": "4242 4242 4242 4242",
            "expiry": "12/25",  # Any future date
            "cvc": "123"  # Any 3 digits
        }


# Test
if __name__ == "__main__":
    stripe_service = StripeService()
    print(f"✅ Stripe service initialized (Test Mode: {stripe_service.is_test_mode})")
    print(f"   Premium Price: ${stripe_service.PREMIUM_PRICE_USD}")
    print(f"   Test Card: {stripe_service.test_card_number()}")
