"""
Vitality Score Integration Layer
──────────────────────────────────

Wires the APIManager (polite-pacing + error handling) into the existing
vitality_score.py engine.

This is a thin adapter that:
1. Intercepts API calls from vitality_score
2. Applies polite-pacing + local error recovery
3. Returns results or "System Cooling Down" state
4. Persists failed requests for later retry

Integration points:
- call_api_with_backoff() → managed_api_call()
- analyse_listing() → analyse_listing_managed()
"""

import json
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

from api_manager import APIManager, APIRequest, RateLimitError

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBAL API MANAGER INSTANCE
# ─────────────────────────────────────────────────────────────

_api_manager: Optional[APIManager] = None


def get_api_manager(pacing_delay: float = 5) -> APIManager:
    """Get or create the global API manager."""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager(pacing_delay=pacing_delay)
    return _api_manager


# ─────────────────────────────────────────────────────────────
# ERROR STATES FOR UI
# ─────────────────────────────────────────────────────────────

SYSTEM_COOLING_DOWN = {
    "status": "cooling_down",
    "message": (
        "🌡️  System Cooling Down\n"
        "We've hit a rate limit. Your request is safely queued and will "
        "resume automatically. Check back in 5 minutes."
    ),
    "user_action": "wait_and_retry",
    "vitality_score": None,
    "grade": None,
    "summary": "Analysis paused due to API rate limit. Please try again shortly.",
}

SYSTEM_ERROR = {
    "status": "error",
    "message": (
        "⚠️  System Temporary Error\n"
        "We encountered an issue, but your request is safely stored. "
        "We'll automatically retry. Check back shortly."
    ),
    "user_action": "wait_and_retry",
    "vitality_score": None,
    "grade": None,
    "summary": "Analysis failed. Our system is working to recover.",
}


# ─────────────────────────────────────────────────────────────
# MANAGED API CALL (DROP-IN REPLACEMENT FOR call_api_with_backoff)
# ─────────────────────────────────────────────────────────────

def managed_api_call(
    messages: list,
    max_tokens: int = 3000,
    label: str = "API",
    request_id: Optional[str] = None,
    on_cooling_down: Optional[callable] = None
) -> Optional[str]:
    """
    Drop-in replacement for call_api_with_backoff() from vitality_score.py

    Enforces polite-pacing between calls, queues failed requests locally.

    Args:
        messages: OpenAI chat messages
        max_tokens: Max tokens in response
        label: Human-readable label for logging
        request_id: Unique request ID (auto-generated if None)
        on_cooling_down: Callback if API rate-limited (signature: lambda -> None)

    Returns:
        str: API response on success
        None: if API failed + queued (app should show "System Cooling Down")
    """
    manager = get_api_manager()

    if request_id is None:
        request_id = f"{label}_{int(datetime.utcnow().timestamp()*1000)}"

    try:
        # Make the actual API call (polite-pacing enforced by manager)
        # In production, swap this with your real OpenAI/API client
        response = _execute_managed_api(
            messages=messages,
            max_tokens=max_tokens,
            label=label,
            request_id=request_id
        )
        return response

    except RateLimitError as e:
        logger.warning(f"[{request_id}] Rate limit hit: {e}")
        manager._handle_rate_limit(APIRequest(
            id=request_id,
            endpoint="vitality_score",
            payload={"messages": messages, "max_tokens": max_tokens},
            status="cooling_down",
            created_at=datetime.utcnow().isoformat(),
            error_message=str(e)
        ))
        if on_cooling_down:
            on_cooling_down()
        return None

    except Exception as e:
        logger.error(f"[{request_id}] API error: {e}")
        manager._handle_general_error(APIRequest(
            id=request_id,
            endpoint="vitality_score",
            payload={"messages": messages, "max_tokens": max_tokens},
            status="error",
            created_at=datetime.utcnow().isoformat(),
            error_message=str(e)
        ), str(e))
        return None


def _execute_managed_api(
    messages: list,
    max_tokens: int,
    label: str,
    request_id: str
) -> str:
    """
    Actually execute the API call.
    This is the swap point for your real OpenAI client.

    In production, this would look like:

        from openai import OpenAI, RateLimitError
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    """
    raise NotImplementedError(
        "Implement _execute_managed_api() to call your actual API client. "
        "See comments above for OpenAI example."
    )


# ─────────────────────────────────────────────────────────────
# WRAPPED analyse_listing — DROP-IN REPLACEMENT
# ─────────────────────────────────────────────────────────────

def analyse_listing_managed(
    image_paths: list[str],
    location: str,
    budget: float,
    currency: str = "RM",
    listing_type: str = "city_apartment",
    corrections: str = "",
    guest_report: str = "",
    competitor_avg_score: Optional[float] = None,
    shopping_preference: str = "both",
    goal: str = "all",
    on_cooling_down: Optional[callable] = None
) -> dict:
    """
    Wrapped version of analyse_listing() that applies error handling.

    If API rate-limits or errors out:
        - Returns SYSTEM_COOLING_DOWN or SYSTEM_ERROR
        - Queues request locally for automatic retry
        - App displays user-friendly message instead of crashing

    Usage:
        report = analyse_listing_managed(
            image_paths=[...],
            location="Ampang, Malaysia",
            budget=1500,
            currency="RM",
            on_cooling_down=lambda: ui.show_cooling_down_banner()
        )
        if report["status"] == "cooling_down":
            ui.show_message(report["message"])
        else:
            ui.display_vitality_report(report)
    """
    # Import here to avoid circular dependency
    try:
        from vitality_score import analyse_listing
    except ImportError:
        logger.error("Could not import analyse_listing from vitality_score")
        return SYSTEM_ERROR

    try:
        # Patch call_api_with_backoff for this call
        import vitality_score
        original_call = vitality_score.call_api_with_backoff

        def patched_call(messages, max_tokens=3000, label="API"):
            return managed_api_call(
                messages=messages,
                max_tokens=max_tokens,
                label=label,
                on_cooling_down=on_cooling_down
            )

        vitality_score.call_api_with_backoff = patched_call

        # Run analysis with patched API call
        report = analyse_listing(
            image_paths=image_paths,
            location=location,
            budget=budget,
            currency=currency,
            listing_type=listing_type,
            corrections=corrections,
            guest_report=guest_report,
            competitor_avg_score=competitor_avg_score,
            shopping_preference=shopping_preference,
            goal=goal
        )

        # Add status field for UI
        if report:
            report["status"] = "success"
        return report

    except Exception as e:
        logger.error(f"analyse_listing_managed failed: {e}")
        # Return error state instead of crashing
        error_response = SYSTEM_ERROR.copy()
        error_response["error_details"] = str(e)
        return error_response

    finally:
        # Restore original function
        try:
            vitality_score.call_api_with_backoff = original_call
        except:
            pass


# ─────────────────────────────────────────────────────────────
# QUEUE MONITORING & DIAGNOSTICS
# ─────────────────────────────────────────────────────────────

def get_queue_status() -> dict:
    """Return current queue status for UI dashboard."""
    manager = get_api_manager()
    return manager.get_queue_status()


def retry_failed_requests() -> dict:
    """
    Manually trigger retry of all queued requests.
    Useful for background job or user-initiated "retry" button.

    Returns: {success: count, failed: count, cooling_down: count}
    """
    manager = get_api_manager()
    queue = manager.queue.get_all()

    results = {"success": 0, "failed": 0, "cooling_down": 0}

    for request in queue:
        if request.status in ("pending", "cooling_down"):
            try:
                # Retry the request
                response = _execute_managed_api(
                    messages=request.payload.get("messages", []),
                    max_tokens=request.payload.get("max_tokens", 3000),
                    label="Retry",
                    request_id=request.id
                )
                request.status = "success"
                request.result = json.loads(response)
                results["success"] += 1
                logger.info(f"[{request.id}] Retry succeeded")
                manager.queue.remove(request.id)

            except RateLimitError:
                request.status = "cooling_down"
                results["cooling_down"] += 1
                logger.warning(f"[{request.id}] Retry hit rate limit again")
                manager.queue.update(request)

            except Exception as e:
                request.attempt_count += 1
                if request.attempt_count >= 4:
                    request.status = "failed"
                    results["failed"] += 1
                    logger.error(f"[{request.id}] Permanent retry failure")
                    manager.queue.remove(request.id)
                else:
                    request.status = "cooling_down"
                    results["cooling_down"] += 1
                    logger.warning(f"[{request.id}] Retry failed, will retry again")
                    manager.queue.update(request)

    return results


# ─────────────────────────────────────────────────────────────
# EXAMPLE USAGE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout
    )

    manager = get_api_manager()
    print("✅ Integration layer initialized")
    print(f"   Polite-pacing: {manager.pacing_delay}s")
    print(f"   Queue status: {manager.get_queue_status()}")
    print("\nReady to wrap vitality_score.analyse_listing()")
    print("Usage: report = analyse_listing_managed(...)")
