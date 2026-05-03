"""
🔐 ANTI-ABUSE PROTOCOL: Digital Moat for Free Tier Protection

4-Layer Defense System:
1. Email Normalization & Burner Block
2. URL ID Extraction & 30-Day Duplicate Block
3. Image Fingerprinting (MD5/SHA256)
4. IP Rate Limiting (1 report per IP per 30 days)

Prevents:
- Burner email abuse
- Repeated property audits with disposable emails
- Duplicate photo uploads (different URLs, same images)
- Distributed attack via multiple IPs
"""

import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from urllib.parse import urlparse, parse_qs
import sqlite3

logger = logging.getLogger(__name__)

# ============================================================================
# LAYER 1: EMAIL NORMALIZATION & BURNER BLOCK
# ============================================================================

# Common disposable email domains (burner emails)
BURNER_EMAIL_DOMAINS = {
    # Temporary email services
    'tempmail.com', '10minutemail.com', 'guerrillamail.com',
    'mailinator.com', 'temp-mail.org', 'throwaway.email',
    'fakeinbox.com', 'trashmail.com', '33mail.com',
    'yopmail.com', 'maildrop.cc', 'temp.email',
    'sharklasers.com', 'grr.la', 'getnada.com',
    
    # Testing/spam domains
    'test.com', 'example.com', 'test.co', 'spam4.me',
    
    # Catch-all/proxy services
    'temp-mail.io', '1secmail.com', 'mytrashmail.com',
}

def normalize_email(email: str) -> str:
    """
    🔐 LAYER 1A: Normalize email to prevent alias abuse
    
    Gmail: user+tag@gmail.com → user@gmail.com
    Gmail: user.name@gmail.com → username@gmail.com (periods ignored by Gmail)
    
    Args:
        email: Raw email from form
    
    Returns:
        Normalized email for database lookup
    """
    email = email.lower().strip()
    
    # Gmail normalization
    if email.endswith('@gmail.com'):
        # Remove everything after + (alias tags)
        base = email.split('+')[0]
        # Remove all periods (Gmail ignores them)
        base = base.replace('.', '')
        return f"{base}@gmail.com"
    
    # Google Workspace (gsuite)
    if email.endswith('@googlemail.com'):
        base = email.split('+')[0].replace('.', '')
        return f"{base}@googlemail.com"
    
    # Other domains: just normalize case and remove + aliases
    if '+' in email:
        local, domain = email.rsplit('@', 1)
        local = local.split('+')[0]
        return f"{local}@{domain}"
    
    return email


def is_burner_email(email: str) -> bool:
    """
    🔐 LAYER 1B: Block disposable/burner email domains
    
    Args:
        email: Email to check
    
    Returns:
        True if burner domain detected
    """
    email = email.lower().strip()
    
    try:
        domain = email.split('@')[1]
        
        # Check against burner list
        if domain in BURNER_EMAIL_DOMAINS:
            logger.warning(f"🔐 BLOCKED: Burner email domain detected: {domain}")
            return True
        
        # Check for suspicious patterns
        if domain.startswith('temp') or domain.startswith('trash'):
            logger.warning(f"🔐 BLOCKED: Suspicious email domain pattern: {domain}")
            return True
        
        return False
    except:
        return False


# ============================================================================
# LAYER 2: URL ID EXTRACTION & 30-DAY DUPLICATE BLOCK
# ============================================================================

def extract_listing_id(url: str) -> Optional[str]:
    """
    🔐 LAYER 2A: Extract Property ID from Airbnb/VRBO URLs
    
    Airbnb: https://www.airbnb.com/rooms/12345678?params=value
            → Extract "12345678" (room ID)
    
    VRBO: https://www.vrbo.com/123456?params=value
          → Extract "123456" (property ID)
    
    Args:
        url: Listing URL
    
    Returns:
        Property ID or None if not found
    """
    try:
        # Remove query parameters
        clean_url = url.split('?')[0].strip('/')
        
        # Airbnb pattern: /rooms/{ID}
        airbnb_match = re.search(r'/rooms/(\d+)', clean_url)
        if airbnb_match:
            listing_id = airbnb_match.group(1)
            logger.info(f"📍 Extracted Airbnb ID: {listing_id}")
            return listing_id
        
        # VRBO pattern: /{ID} (last number in path)
        vrbo_match = re.search(r'vrbo\.com/(\d+)', clean_url)
        if vrbo_match:
            listing_id = vrbo_match.group(1)
            logger.info(f"📍 Extracted VRBO ID: {listing_id}")
            return listing_id
        
        logger.warning(f"⚠️  Could not extract listing ID from URL: {url}")
        return None
    except Exception as e:
        logger.error(f"❌ URL parsing error: {e}")
        return None


def check_duplicate_listing_30days(db, listing_id: str) -> bool:
    """
    🔐 LAYER 2B: Check if property ID was already audited in last 30 days
    
    Prevents: Users resubmitting same property on Free Tier
    (Forces them to upgrade for multiple audits of same property)
    
    Args:
        db: Database connection
        listing_id: Property ID to check
    
    Returns:
        True if duplicate found in last 30 days
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check form_submissions for matching listing_id in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        cursor.execute("""
            SELECT COUNT(*) FROM form_submissions
            WHERE airbnb_url LIKE ?
            AND created_at > ?
            AND report_type = 'free'
        """, (f"%{listing_id}%", thirty_days_ago.isoformat()))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.warning(f"🔐 BLOCKED: Property {listing_id} already audited in last 30 days (Free Tier)")
            return True
        
        logger.info(f"✅ Property {listing_id} not audited in last 30 days")
        return False
    except Exception as e:
        logger.error(f"❌ Duplicate check error: {e}")
        return False


# ============================================================================
# LAYER 3: IMAGE FINGERPRINTING (MD5/SHA256)
# ============================================================================

def hash_image_file(file_path: str, algorithm: str = 'sha256') -> str:
    """
    🔐 LAYER 3A: Generate cryptographic hash of image file
    
    Prevents: Same image uploaded under different filenames
    
    Args:
        file_path: Path to image file
        algorithm: 'md5' or 'sha256'
    
    Returns:
        Hex hash string
    """
    try:
        if algorithm == 'md5':
            hasher = hashlib.md5()
        else:
            hasher = hashlib.sha256()
        
        # Read file in chunks (memory efficient)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        hash_hex = hasher.hexdigest()
        logger.info(f"📷 Image hash ({algorithm}): {hash_hex[:16]}...")
        return hash_hex
    except Exception as e:
        logger.error(f"❌ Image hashing error: {e}")
        return ""


def check_duplicate_image(db, image_hash: str, report_type: str = 'free') -> bool:
    """
    🔐 LAYER 3B: Check if image hash was previously processed
    
    Prevents: Reusing images across different Free Tier submissions
    
    Args:
        db: Database connection
        image_hash: SHA256 hash of image
        report_type: 'free' or 'premium'
    
    Returns:
        True if duplicate hash found
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check processed_images table for matching hash
        cursor.execute("""
            SELECT COUNT(*) FROM processed_images
            WHERE image_hash = ?
            AND report_type = ?
        """, (image_hash, report_type))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.warning(f"🔐 BLOCKED: Duplicate image hash detected (Free Tier)")
            return True
        
        logger.info(f"✅ Image hash not previously processed")
        return False
    except Exception as e:
        logger.error(f"❌ Image duplicate check error: {e}")
        return False


def store_image_hash(db, image_hash: str, submission_id: int, file_name: str, report_type: str = 'free'):
    """
    🔐 LAYER 3C: Store image hash for future duplicate detection
    
    Args:
        db: Database connection
        image_hash: SHA256 hash
        submission_id: Form submission ID
        file_name: Original filename
        report_type: 'free' or 'premium'
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO processed_images
            (image_hash, submission_id, file_name, report_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (image_hash, submission_id, file_name, report_type, datetime.now().isoformat()))
        
        conn.commit()
        logger.info(f"📷 Stored image hash: {image_hash[:16]}...")
    except Exception as e:
        logger.error(f"❌ Error storing image hash: {e}")


# ============================================================================
# LAYER 4: IP RATE LIMITING (1 free report per IP per 30 days)
# ============================================================================

def get_client_ip(request) -> str:
    """
    Extract client IP from FastAPI request
    
    Checks: X-Forwarded-For (proxy), X-Real-IP (nginx), client.host
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Client IP address
    """
    # Check proxy headers (VPS/nginx)
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    
    x_real_ip = request.headers.get('x-real-ip')
    if x_real_ip:
        return x_real_ip.strip()
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


def check_ip_rate_limit(db, client_ip: str, report_type: str = 'free') -> Tuple[bool, int]:
    """
    🔐 LAYER 4A: Check if IP already submitted free report in last 30 days
    
    Prevents: Distributed attacks via multiple IPs
    Limit: 1 free report per IP per 30-day rolling window
    
    Args:
        db: Database connection
        client_ip: Client IP address
        report_type: 'free' or 'premium' (only limit free)
    
    Returns:
        Tuple: (is_blocked: bool, reports_submitted: int)
    """
    if report_type != 'free':
        # Premium tier not rate limited
        return False, 0
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check IP rate limit table
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        cursor.execute("""
            SELECT COUNT(*) FROM ip_rate_limits
            WHERE client_ip = ?
            AND report_type = 'free'
            AND created_at > ?
        """, (client_ip, thirty_days_ago.isoformat()))
        
        count = cursor.fetchone()[0]
        
        if count >= 1:
            logger.warning(f"🔐 BLOCKED: IP {client_ip} already submitted 1+ free reports in 30 days")
            return True, count
        
        logger.info(f"✅ IP {client_ip} under rate limit (1/30 days)")
        return False, count
    except Exception as e:
        logger.error(f"❌ IP rate limit check error: {e}")
        return False, 0


def store_ip_access(db, client_ip: str, submission_id: int, report_type: str = 'free'):
    """
    🔐 LAYER 4B: Store IP access record for rate limiting
    
    Args:
        db: Database connection
        client_ip: Client IP
        submission_id: Form submission ID
        report_type: 'free' or 'premium'
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ip_rate_limits
            (client_ip, submission_id, report_type, created_at)
            VALUES (?, ?, ?, ?)
        """, (client_ip, submission_id, report_type, datetime.now().isoformat()))
        
        conn.commit()
        logger.info(f"🔐 Recorded IP access: {client_ip}")
    except Exception as e:
        logger.error(f"❌ Error storing IP access: {e}")


# ============================================================================
# COMPREHENSIVE ANTI-ABUSE CHECK (All 4 Layers)
# ============================================================================

def run_anti_abuse_check(db, email: str, airbnb_url: str, client_ip: str, 
                        report_type: str = 'free') -> Tuple[bool, str]:
    """
    🔐 ANTI-ABUSE PROTOCOL: Run all 4 layers of defense
    
    Returns: (blocked: bool, reason: str)
    
    Args:
        db: Database connection
        email: User email
        airbnb_url: Listing URL
        client_ip: Client IP
        report_type: 'free' or 'premium'
    
    Returns:
        Tuple: (True, reason) if blocked, (False, "OK") if allowed
    """
    
    # Layer 1: Email checks (burner + normalization)
    if is_burner_email(email):
        return True, "❌ Burner email detected. Please use a real email address."
    
    normalized_email = normalize_email(email)
    logger.info(f"📧 Normalized email: {email} → {normalized_email}")
    
    # Layer 2: URL duplicate check (for free tier only)
    if report_type == 'free' and airbnb_url:
        listing_id = extract_listing_id(airbnb_url)
        if listing_id and check_duplicate_listing_30days(db, listing_id):
            return True, f"❌ This property was already audited in the last 30 days. Upgrade to Premium for unlimited audits."
    
    # Layer 4: IP rate limiting (for free tier only)
    if report_type == 'free':
        is_blocked, count = check_ip_rate_limit(db, client_ip, report_type)
        if is_blocked:
            return True, f"❌ Free tier limited to 1 report per IP per 30 days. You've already submitted {count}. Upgrade to Premium for unlimited reports."
    
    # All checks passed
    logger.info(f"✅ PASSED anti-abuse checks: {normalized_email} from {client_ip}")
    return False, "OK"
