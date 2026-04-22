"""
Phase 2 Test Suite — Automated Flow Testing

Tests:
- Form submission
- Email verification
- Free report generation
- Premium payment flow
- Webhook handling
- Report delivery tracking
"""

import requests
import json
import time
import re
from datetime import datetime
import sqlite3

# Configuration
API_BASE = "http://localhost:8000"
DB_PATH = "design_diagnosis.db"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def log_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")


def log_error(msg):
    print(f"{RED}❌ {msg}{RESET}")


def log_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")


def log_test(msg):
    print(f"\n{YELLOW}» {msg}{RESET}")


def get_db_value(query):
    """Query database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        log_error(f"DB query failed: {e}")
        return None


def get_verification_token(submission_id):
    """Extract verification token from database"""
    result = get_db_value(
        f"SELECT token FROM email_verifications WHERE submission_id = {submission_id}"
    )
    return result[0] if result else None


def test_health_check():
    """Test 1: Health check"""
    log_test("Health Check")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["phase"] == "2"
        log_success(f"Health check passed (services: {data['services']})")
        return True
    except Exception as e:
        log_error(f"Health check failed: {e}")
        return False


def test_free_report_flow():
    """Test 2: Complete free report flow"""
    log_test("Free Report Flow")
    
    # Step 1: Submit form
    log_info("Submitting free report form...")
    
    form_data = {
        "email": f"test_free_{int(time.time())}@example.com",
        "property_name": f"Test Property Free {int(time.time())}",
        "airbnb_url": "https://www.airbnb.com/rooms/12345",
        "listing_type": "House",
        "bedrooms": 3,
        "bathrooms": 2,
        "guest_capacity": 6,
        "total_photos": "11-15",
        "guest_comfort_checklist": ["wifi", "linens", "coffee"],
        "report_type": "free"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/submit-form", json=form_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "verification_pending"
        
        submission_id = data["submission_id"]
        log_success(f"Form submitted (submission_id: {submission_id})")
    except Exception as e:
        log_error(f"Form submission failed: {e}")
        return False
    
    # Step 2: Get verification token
    log_info("Retrieving verification token...")
    time.sleep(0.5)  # Wait for DB write
    
    token = get_verification_token(submission_id)
    if not token:
        log_error("Failed to retrieve verification token")
        return False
    
    log_success(f"Token retrieved: {token[:8]}...")
    
    # Step 3: Verify email
    log_info("Verifying email...")
    
    try:
        response = requests.get(f"{API_BASE}/api/verify-email?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "generating"
        
        log_success("Email verified, report generating...")
    except Exception as e:
        log_error(f"Email verification failed: {e}")
        return False
    
    # Step 4: Wait for report generation and check database
    log_info("Waiting for report generation (5 seconds)...")
    time.sleep(5)
    
    try:
        result = get_db_value(f"SELECT id FROM report_deliveries WHERE submission_id = {submission_id}")
        if result:
            log_success("Report generated and delivery record created")
            return True
        else:
            log_error("Report delivery record not found")
            return False
    except Exception as e:
        log_error(f"Failed to check report: {e}")
        return False


def test_premium_payment_flow():
    """Test 3: Complete premium payment flow"""
    log_test("Premium Payment Flow")
    
    # Step 1: Submit form (premium)
    log_info("Submitting premium report form...")
    
    form_data = {
        "email": f"test_premium_{int(time.time())}@example.com",
        "property_name": f"Test Property Premium {int(time.time())}",
        "listing_type": "Apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "guest_capacity": 4,
        "total_photos": "21-30",
        "guest_comfort_checklist": ["wifi", "linens", "coffee", "ac", "tv"],
        "report_type": "premium"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/submit-form", json=form_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        submission_id = data["submission_id"]
        log_success(f"Premium form submitted (submission_id: {submission_id})")
    except Exception as e:
        log_error(f"Form submission failed: {e}")
        return False
    
    # Step 2: Get and verify email
    log_info("Verifying email...")
    time.sleep(0.5)
    
    token = get_verification_token(submission_id)
    if not token:
        log_error("Failed to retrieve token")
        return False
    
    try:
        response = requests.get(f"{API_BASE}/api/verify-email?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "payment_required"
        
        log_success("Email verified, ready for payment")
    except Exception as e:
        log_error(f"Email verification failed: {e}")
        return False
    
    # Step 3: Create payment intent
    log_info("Creating payment intent...")
    
    payment_data = {
        "submission_id": submission_id,
        "property_name": form_data["property_name"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/create-payment", json=payment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        payment_intent_id = data["payment_intent_id"]
        log_success(f"Payment intent created: {payment_intent_id[:20]}...")
    except Exception as e:
        log_error(f"Payment intent creation failed: {e}")
        return False
    
    # Step 4: Simulate webhook
    log_info("Simulating Stripe webhook...")
    
    webhook_data = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": payment_intent_id,
                "status": "succeeded",
                "metadata": {
                    "submission_id": submission_id
                }
            }
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/payment-webhook",
            json=webhook_data,
            headers={"Stripe-Signature": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["received"] == True
        
        log_success("Webhook processed successfully")
    except Exception as e:
        log_error(f"Webhook processing failed: {e}")
        return False
    
    # Step 5: Wait and verify payment status
    log_info("Waiting for report generation (5 seconds)...")
    time.sleep(5)
    
    try:
        # Check payment status
        result = get_db_value(
            f"SELECT status FROM payments WHERE stripe_payment_intent_id = '{payment_intent_id}'"
        )
        if result and result[0] == "succeeded":
            log_success("Payment marked as succeeded")
        else:
            log_error("Payment status not updated")
            return False
        
        # Check report delivery
        result = get_db_value(f"SELECT id FROM report_deliveries WHERE submission_id = {submission_id}")
        if result:
            log_success("Premium report generated and delivery record created")
            return True
        else:
            log_error("Premium report delivery record not found")
            return False
    except Exception as e:
        log_error(f"Failed to verify: {e}")
        return False


def test_email_verification_endpoints():
    """Test 4: Email verification edge cases"""
    log_test("Email Verification Edge Cases")
    
    # Invalid token
    log_info("Testing invalid token...")
    
    try:
        response = requests.get(f"{API_BASE}/api/verify-email?token=invalid_token_12345")
        assert response.status_code == 404
        log_success("Invalid token correctly rejected")
    except Exception as e:
        log_error(f"Invalid token test failed: {e}")
        return False
    
    return True


def test_database_integrity():
    """Test 5: Database schema and data integrity"""
    log_test("Database Integrity")
    
    try:
        # Check tables exist
        tables = ["form_submissions", "email_verifications", "payments", "report_deliveries"]
        
        for table in tables:
            result = get_db_value(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if result:
                log_success(f"Table '{table}' exists")
            else:
                log_error(f"Table '{table}' missing")
                return False
        
        return True
    except Exception as e:
        log_error(f"Database integrity check failed: {e}")
        return False


def test_form_validation():
    """Test 6: Form validation"""
    log_test("Form Validation")
    
    # Missing required fields
    log_info("Testing missing email...")
    
    invalid_data = {
        "email": "",  # Missing
        "property_name": "Test",
        "listing_type": "House",
        "bedrooms": 1,
        "bathrooms": 1,
        "guest_capacity": 2,
        "total_photos": "11-15",
        "guest_comfort_checklist": [],
        "report_type": "free"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/submit-form", json=invalid_data)
        assert response.status_code == 400
        log_success("Invalid email correctly rejected")
    except Exception as e:
        log_error(f"Form validation test failed: {e}")
        return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BLUE}Phase 2 Test Suite{RESET}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    
    log_info(f"API Base: {API_BASE}")
    log_info(f"Database: {DB_PATH}\n")
    
    results = {
        "Health Check": test_health_check(),
        "Database Integrity": test_database_integrity(),
        "Form Validation": test_form_validation(),
        "Email Verification": test_email_verification_endpoints(),
        "Free Report Flow": test_free_report_flow(),
        "Premium Payment Flow": test_premium_payment_flow(),
    }
    
    print(f"\n{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BLUE}Test Results{RESET}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name:<30} {status}")
    
    print(f"\n{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{GREEN}✅ All tests passed!{RESET}\n")
        return 0
    else:
        print(f"{RED}❌ Some tests failed{RESET}\n")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
