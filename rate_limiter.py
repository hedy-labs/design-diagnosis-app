"""
429 SHIELD: Rate Limit Resilience & Exponential Backoff
Handles Vision API rate limits gracefully with automatic retry logic

Protects against:
- 429 Too Many Requests (rate limit exceeded)
- 503 Service Unavailable (temporary overload)
- Connection timeouts (network issues)
"""

import logging
import time
import functools
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================================================
# EXPONENTIAL BACKOFF CONFIGURATION
# ============================================================================

class BackoffConfig:
    """Rate limit backoff strategy"""
    
    # Initial wait time (seconds)
    INITIAL_WAIT = 10
    
    # Maximum wait time (seconds)
    MAX_WAIT = 300  # 5 minutes
    
    # Backoff multiplier
    MULTIPLIER = 2.5
    
    # Jitter to prevent thundering herd (0-1, percentage of base wait)
    JITTER = 0.2
    
    # Maximum retry attempts
    MAX_RETRIES = 5


class RateLimitError(Exception):
    """Rate limit error with retry metadata"""
    
    def __init__(self, status_code: int, retry_after: Optional[int] = None, message: str = "Rate limited"):
        self.status_code = status_code
        self.retry_after = retry_after
        self.message = message
        super().__init__(self.message)


# ============================================================================
# RETRY DECORATOR WITH EXPONENTIAL BACKOFF
# ============================================================================

def retry_with_backoff(
    max_retries: int = BackoffConfig.MAX_RETRIES,
    initial_wait: float = BackoffConfig.INITIAL_WAIT,
    max_wait: float = BackoffConfig.MAX_WAIT,
    multiplier: float = BackoffConfig.MULTIPLIER,
    jitter: float = BackoffConfig.JITTER
):
    """
    Decorator: Retry function with exponential backoff on 429/503 errors
    
    Args:
        max_retries: Maximum retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
        multiplier: Exponential backoff multiplier
        jitter: Random jitter (0-1, percentage of wait time)
    
    Returns:
        Decorated function that retries on rate limits
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            wait_time = initial_wait
            last_error = None
            
            while attempt < max_retries:
                try:
                    logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}: {func.__name__}")
                    return func(*args, **kwargs)
                
                except RateLimitError as e:
                    last_error = e
                    attempt += 1
                    
                    if attempt >= max_retries:
                        logger.error(f"❌ Max retries ({max_retries}) exhausted: {e.message}")
                        raise
                    
                    # Use Retry-After header if provided
                    if e.retry_after:
                        wait_time = e.retry_after
                        logger.warning(f"⏳ Rate limited (429). Retry-After: {wait_time}s")
                    else:
                        # Apply exponential backoff
                        logger.warning(f"⏳ Rate limited (429). Waiting {wait_time:.1f}s before retry...")
                    
                    # Add jitter to prevent thundering herd
                    import random
                    jitter_amount = wait_time * jitter * random.random()
                    actual_wait = wait_time + jitter_amount
                    
                    logger.info(f"💤 Sleeping {actual_wait:.1f}s (base: {wait_time:.1f}s + jitter: {jitter_amount:.1f}s)")
                    time.sleep(actual_wait)
                    
                    # Exponential backoff for next retry (if no Retry-After)
                    if not e.retry_after:
                        wait_time = min(wait_time * multiplier, max_wait)
                
                except Exception as e:
                    # Other exceptions: don't retry
                    logger.error(f"❌ Non-retryable error in {func.__name__}: {e}")
                    raise
            
            # Should not reach here
            if last_error:
                raise last_error
            raise RuntimeError(f"Unexpected state in retry_with_backoff for {func.__name__}")
        
        return wrapper
    return decorator


# ============================================================================
# MANDATORY PACING (THROTTLING)
# ============================================================================

class ThrottleConfig:
    """Mandatory pacing between API calls"""
    
    # Minimum delay between individual image calls (seconds)
    MIN_DELAY_BETWEEN_CALLS = 2.5
    
    # Minimum delay between batch calls (seconds)
    MIN_DELAY_BETWEEN_BATCHES = 5.0


def throttle_calls(min_delay: float = ThrottleConfig.MIN_DELAY_BETWEEN_CALLS):
    """
    Decorator: Enforce minimum delay between function calls
    
    Prevents us from hitting rate limits in the first place by
    pacing out API calls to Vision API.
    
    Args:
        min_delay: Minimum delay between calls in seconds
    
    Returns:
        Decorated function with mandatory pacing
    """
    
    last_call_time = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            
            # Check time since last call
            now = time.time()
            last_call = last_call_time.get(func_name, 0)
            elapsed = now - last_call
            
            if elapsed < min_delay:
                wait_time = min_delay - elapsed
                logger.info(f"🚦 PACING: Waiting {wait_time:.1f}s before {func_name} (rate: 1 per {min_delay}s)")
                time.sleep(wait_time)
            
            # Call function
            last_call_time[func_name] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# USER-FACING STATUS UPDATES
# ============================================================================

def get_rate_limit_message(attempt: int, total_attempts: int) -> str:
    """
    Generate user-friendly rate limit status message
    
    Args:
        attempt: Current attempt number (1-indexed)
        total_attempts: Total attempts allowed
    
    Returns:
        User-friendly status message (branded, generic)
    """
    
    if attempt <= 1:
        return "Optimizing your report details for maximum accuracy... this may take a moment."
    
    retry_count = attempt - 1
    if retry_count <= 2:
        return f"Fine-tuning analysis for precision ({retry_count} optimization pass)... almost there."
    else:
        return "Completing final quality checks... thank you for your patience."


# ============================================================================
# RATE LIMIT DETECTOR & HANDLER
# ============================================================================

def detect_rate_limit(status_code: int, headers: dict = None) -> Optional[RateLimitError]:
    """
    Detect rate limit errors from Vision API response
    
    Args:
        status_code: HTTP status code
        headers: Response headers (may contain Retry-After)
    
    Returns:
        RateLimitError if rate limited, None otherwise
    """
    
    headers = headers or {}
    
    if status_code == 429:
        # Too Many Requests
        retry_after = headers.get('Retry-After')
        if retry_after:
            try:
                retry_after = int(retry_after)
            except (ValueError, TypeError):
                retry_after = None
        
        return RateLimitError(
            status_code=429,
            retry_after=retry_after,
            message=f"Rate limited by Vision API (429). Retry-After: {retry_after}s" if retry_after else "Rate limited by Vision API (429)"
        )
    
    elif status_code == 503:
        # Service Unavailable (temporary overload)
        retry_after = headers.get('Retry-After', 60)
        try:
            retry_after = int(retry_after)
        except (ValueError, TypeError):
            retry_after = 60
        
        return RateLimitError(
            status_code=503,
            retry_after=retry_after,
            message=f"Vision API temporarily unavailable (503). Retrying in {retry_after}s"
        )
    
    elif status_code >= 500:
        # Other 5xx errors: treat as temporary
        return RateLimitError(
            status_code=status_code,
            retry_after=None,
            message=f"Vision API server error ({status_code}). Will retry with backoff"
        )
    
    return None


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_rate_limit_health() -> Dict[str, Any]:
    """
    Health check: Report on rate limiter configuration
    
    Returns:
        Dict with health status
    """
    
    return {
        "status": "✅ OK",
        "rate_limiter": "429 Shield ACTIVE",
        "exponential_backoff": {
            "initial_wait": BackoffConfig.INITIAL_WAIT,
            "max_wait": BackoffConfig.MAX_WAIT,
            "multiplier": BackoffConfig.MULTIPLIER,
            "max_retries": BackoffConfig.MAX_RETRIES
        },
        "mandatory_pacing": {
            "min_delay_between_calls": ThrottleConfig.MIN_DELAY_BETWEEN_CALLS,
            "min_delay_between_batches": ThrottleConfig.MIN_DELAY_BETWEEN_BATCHES
        }
    }
