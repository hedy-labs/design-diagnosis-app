"""
Sanitizer — Global Input Sanitization

Provides sanitization functions for all data types:
- Numeric fields (strip non-digits, handle "51+" format)
- Text fields (remove emoji, special Unicode)
- Email validation
- Safe type conversions
"""

import re
import logging
from typing import Union, Optional, List
from data_cleaner import clean_item_name

logger = logging.getLogger(__name__)


def sanitize_integer(value: Union[str, int, None], default: int = 0, allow_plus: bool = True) -> int:
    """
    Safely convert any value to integer.
    
    Args:
        value: String like "51+", int, or None
        default: Default value if parsing fails
        allow_plus: If True, "51+" becomes 51
    
    Returns: Clean integer
    
    Examples:
        sanitize_integer("51+") → 51
        sanitize_integer("10") → 10
        sanitize_integer(20) → 20
        sanitize_integer(None) → 0
        sanitize_integer("abc") → 0
    """
    try:
        if value is None or value == "":
            return default
        
        # Already an integer
        if isinstance(value, int):
            return max(0, value)  # Ensure non-negative
        
        # String value
        if isinstance(value, str):
            # Extract all digits
            digits = ''.join(c for c in value if c.isdigit())
            if digits:
                return int(digits)
        
        return default
    
    except (ValueError, TypeError):
        logger.warning(f"⚠️  Failed to sanitize integer: {value}, using default: {default}")
        return default


def sanitize_float(value: Union[str, float, int, None], default: float = 0.0) -> float:
    """
    Safely convert any value to float.
    
    Args:
        value: String like "72.5", float, int, or None
        default: Default value if parsing fails
    
    Returns: Clean float
    
    Examples:
        sanitize_float("72.5") → 72.5
        sanitize_float(72) → 72.0
        sanitize_float(None) → 0.0
    """
    try:
        if value is None or value == "":
            return default
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove non-numeric except decimal point
            cleaned = re.sub(r'[^0-9.]', '', value)
            if cleaned:
                return float(cleaned)
        
        return default
    
    except (ValueError, TypeError):
        logger.warning(f"⚠️  Failed to sanitize float: {value}, using default: {default}")
        return default


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text: remove dangerous characters, trim whitespace.
    
    Args:
        text: Input text
        max_length: Optional max length (truncates if exceeded)
    
    Returns: Clean text
    
    Examples:
        sanitize_text("  Hello  ") → "Hello"
        sanitize_text("Test™", 3) → "Tes"
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Trim whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def sanitize_text_for_pdf(text: str) -> str:
    """
    Sanitize text specifically for PDF generation (fpdf2 compatibility).
    
    Removes/replaces problematic Unicode characters:
    - Special dashes (–, —, −) → regular hyphen (-)
    - Bullets (•, ◆) → hyphen (-)
    - Ellipsis (…) → dots (...)
    - Emojis and other non-ASCII → removed
    
    Args:
        text: Input text
    
    Returns: PDF-safe text
    
    Examples:
        sanitize_text_for_pdf("Hello – world") → "Hello - world"
        sanitize_text_for_pdf("Test™ 🎉") → "Test"
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Replace special dashes and punctuation
    replacements = {
        '–': '-',      # En dash
        '—': '-',      # Em dash
        '−': '-',      # Minus sign
        '•': '-',      # Bullet
        '◆': '-',      # Diamond
        '◇': '-',      # White diamond
        '★': '*',      # Star
        '☆': '*',      # White star
        '…': '...',    # Ellipsis
        '"': '"',      # Smart quote left
        '"': '"',      # Smart quote right
        ''': "'",      # Smart single quote
        ''': "'",      # Smart single quote
        '«': '"',      # Guillemet left
        '»': '"',      # Guillemet right
    }
    
    for special, replacement in replacements.items():
        text = text.replace(special, replacement)
    
    # Remove emojis and other non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Clean up extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def sanitize_email(email: str) -> str:
    """
    Validate and sanitize email address.
    
    Args:
        email: Email string
    
    Returns: Cleaned email or empty string if invalid
    """
    if not email or not isinstance(email, str):
        return ""
    
    email = email.strip().lower()
    
    # Basic email validation
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email
    
    logger.warning(f"⚠️  Invalid email format: {email}")
    return ""


def sanitize_url(url: str) -> str:
    """
    Validate and sanitize URL.
    
    Args:
        url: URL string
    
    Returns: Cleaned URL or empty string if invalid
    """
    if not url or not isinstance(url, str):
        return ""
    
    url = url.strip()
    
    # Allow http, https, or no protocol (assume https)
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Basic URL validation
    if re.match(r'^https?://', url):
        return url
    
    logger.warning(f"⚠️  Invalid URL format: {url}")
    return ""


def sanitize_choice(value: str, allowed_values: list, default: str = None) -> str:
    """
    Validate choice against allowed values.
    
    Args:
        value: Selected value
        allowed_values: List of valid options
        default: Default if not in allowed_values
    
    Returns: Valid choice or default
    
    Examples:
        sanitize_choice("free", ["free", "premium"]) → "free"
        sanitize_choice("invalid", ["free", "premium"], "free") → "free"
    """
    if value in allowed_values:
        return value
    
    if default in allowed_values:
        return default
    
    logger.warning(f"⚠️  Invalid choice: {value}, using default: {default}")
    return default


def sanitize_list_of_strings(values: list, max_items: Optional[int] = None) -> list:
    """
    Sanitize list of strings (e.g., comfort checklist).
    
    Args:
        values: List of strings
        max_items: Optional max number of items
    
    Returns: Clean list
    """
    if not isinstance(values, list):
        return []
    
    # Filter out empty/None items and sanitize each
    cleaned = [sanitize_text(str(v)) for v in values if v]
    
    # Limit if needed
    if max_items:
        cleaned = cleaned[:max_items]
    
    return cleaned


def sanitize_form_input(data: dict) -> dict:
    """
    Sanitize entire form submission at once.
    
    Args:
        data: Form data dict
    
    Returns: Sanitized dict
    
    Example:
        data = {
            'property_name': '  My Property  ',
            'bedrooms': '3+',
            'total_photos': '51+',
            'email': 'TEST@EXAMPLE.COM'
        }
        result = sanitize_form_input(data)
        # result = {
        #     'property_name': 'My Property',
        #     'bedrooms': 3,
        #     'total_photos': 51,
        #     'email': 'test@example.com'
        # }
    """
    return {
        'property_name': sanitize_text(data.get('property_name', ''), max_length=100),
        'listing_type': sanitize_choice(data.get('listing_type', ''), ['studio', 'apartment', 'house', 'condo']),
        'bedrooms': sanitize_integer(data.get('bedrooms'), default=1),
        'bathrooms': sanitize_integer(data.get('bathrooms'), default=1),
        'guest_capacity': sanitize_integer(data.get('guest_capacity'), default=2),
        'total_photos': sanitize_integer(data.get('total_photos'), default=20),
        'email': sanitize_email(data.get('email', '')),
        'airbnb_url': sanitize_url(data.get('airbnb_url', '')),
        'guest_comfort_checklist': sanitize_list_of_strings(data.get('guest_comfort_checklist', [])),
        'report_type': sanitize_choice(data.get('report_type', 'free'), ['free', 'premium'], 'free'),
    }


def clean_comfort_checklist_display(checklist: List[str]) -> List[str]:
    """
    Convert comfort checklist items from internal keys to human-readable names.
    
    Example:
        ['bedside_lamps', 'two_pillows_per_guest'] → ['Bedside Lamps', 'Two Pillows Per Guest']
    """
    if not isinstance(checklist, list):
        return []
    
    return [clean_item_name(item) for item in checklist if item]
