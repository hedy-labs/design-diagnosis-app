"""
🔐 INVISIBLE CAPTCHA: Google reCAPTCHA v3 Integration

Zero-friction bot protection:
- No visual puzzles, crosswalks, or user friction
- Runs silently in background (invisible)
- Scores 0.0-1.0 (0 = bot, 1 = human)
- Threshold-based blocking (default 0.5)

Frontend: Executes on form submit
Backend: Validates token + score before processing

Documentation: https://developers.google.com/recaptcha/docs/v3
"""

import logging
import httpx
import os
from typing import Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration from environment
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
RECAPTCHA_THRESHOLD = float(os.getenv("RECAPTCHA_THRESHOLD", "0.5"))
RECAPTCHA_API_URL = "https://www.google.com/recaptcha/api/siteverify"

def get_recaptcha_site_key() -> str:
    """
    Get reCAPTCHA site key for frontend integration
    
    Returns:
        Site key for embedding in HTML
    """
    return RECAPTCHA_SITE_KEY


async def verify_recaptcha_token(token: str, action: str = "submit") -> Tuple[bool, float, Optional[str]]:
    """
    🔐 CAPTCHA VALIDATION: Verify reCAPTCHA v3 token on backend
    
    Args:
        token: Token from frontend (grecaptcha.execute())
        action: Expected action (e.g., 'submit', 'upload')
    
    Returns:
        Tuple: (is_human: bool, score: float, error: Optional[str])
        - is_human: True if score >= threshold
        - score: Confidence score 0.0-1.0
        - error: Error message if validation fails
    
    Scores:
        1.0 = Very likely human
        0.9 = Likely human
        0.5 = Moderate confidence
        0.1 = Likely bot
        0.0 = Very likely bot
    """
    
    # Check if reCAPTCHA configured
    if not RECAPTCHA_SECRET_KEY:
        logger.warning("⚠️  reCAPTCHA not configured (RECAPTCHA_SECRET_KEY missing)")
        return True, 1.0, None  # Fallback: allow if not configured
    
    if not token:
        logger.warning("🔴 CAPTCHA BLOCKED: No token provided")
        return False, 0.0, "Missing CAPTCHA token"
    
    try:
        # Call Google reCAPTCHA API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_API_URL,
                data={
                    "secret": RECAPTCHA_SECRET_KEY,
                    "response": token
                },
                timeout=5.0
            )
        
        if response.status_code != 200:
            logger.error(f"❌ reCAPTCHA API error: {response.status_code}")
            return False, 0.0, "CAPTCHA validation failed (API error)"
        
        data = response.json()
        
        # Check success flag
        if not data.get("success"):
            error_codes = data.get("error-codes", [])
            logger.warning(f"🔴 CAPTCHA FAILED: {error_codes}")
            return False, 0.0, f"CAPTCHA validation failed: {', '.join(error_codes)}"
        
        # Check action matches
        returned_action = data.get("action", "")
        if returned_action != action:
            logger.warning(f"⚠️  Action mismatch: expected '{action}', got '{returned_action}'")
            # Don't block on mismatch, just log it
        
        # Extract confidence score
        score = float(data.get("score", 0.0))
        challenge_ts = data.get("challenge_ts", "")
        hostname = data.get("hostname", "")
        
        logger.info(f"📊 CAPTCHA Score: {score:.2f} (threshold: {RECAPTCHA_THRESHOLD})")
        logger.info(f"   Action: {returned_action}, Hostname: {hostname}, Timestamp: {challenge_ts}")
        
        # Determine if human based on threshold
        is_human = score >= RECAPTCHA_THRESHOLD
        
        if is_human:
            logger.info(f"✅ CAPTCHA PASSED: Score {score:.2f} >= threshold {RECAPTCHA_THRESHOLD}")
            return True, score, None
        else:
            logger.warning(f"🔴 CAPTCHA BLOCKED: Score {score:.2f} < threshold {RECAPTCHA_THRESHOLD}")
            return False, score, f"Bot detection (score: {score:.2f})"
    
    except httpx.TimeoutException:
        logger.error("❌ reCAPTCHA API timeout")
        return False, 0.0, "CAPTCHA validation timeout"
    except Exception as e:
        logger.error(f"❌ reCAPTCHA validation error: {e}")
        return False, 0.0, f"CAPTCHA validation error: {str(e)}"


def get_recaptcha_script() -> str:
    """
    Get HTML script tag for reCAPTCHA v3
    
    Returns:
        HTML script tag to embed in page
    
    Usage in form.html:
        <!-- In <head> -->
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
        
        <!-- Or for Google reCAPTCHA: -->
        <script src="https://www.google.com/recaptcha/api.js"></script>
        <script>
            function onSubmit(token) {
                document.getElementById("form").submit();
            }
        </script>
    """
    
    site_key = get_recaptcha_site_key()
    if not site_key:
        return "<!-- reCAPTCHA not configured -->"
    
    return f"""
    <script src="https://www.google.com/recaptcha/api.js"></script>
    <script>
        window.recaptchaReady = false;
        
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof grecaptcha !== 'undefined') {{
                grecaptcha.ready(function() {{
                    window.recaptchaReady = true;
                    console.log('✅ reCAPTCHA v3 loaded and ready');
                }});
            }}
        }});
        
        async function executeRecaptcha(action = 'submit') {{
            if (!window.recaptchaReady) {{
                console.warn('⚠️  reCAPTCHA not ready yet');
                return null;
            }}
            
            try {{
                const token = await grecaptcha.execute('{site_key}', {{ action }});
                console.log('✅ reCAPTCHA token generated');
                return token;
            }} catch (error) {{
                console.error('❌ reCAPTCHA error:', error);
                return null;
            }}
        }}
    </script>
    """
