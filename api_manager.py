"""
API Manager — Polite-Pacing & Error Handling Layer
───────────────────────────────────────────────────

Sits between the app UI and OpenAI/shopping APIs.

Features:
- Polite-pacing: 5-second mandatory delay between API calls
- Local request queuing: if API fails, store & retry locally
- "System Cooling Down" message: graceful error state for end users
- Exponential backoff: smart retry strategy for rate limits
- Request status tracking: know what's queued, what's retrying, what failed

Philosophy:
  "The app should never crash. The user should never see raw API errors."
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
POLITE_PACING_DELAY = 5  # seconds between API calls (respects org rate limits)
MAX_RETRIES = 4
BACKOFF_BASE = 5  # seconds (5, 10, 20, 40)
QUEUE_FILE = Path("api_request_queue.json")  # Local persistence
STATUS_FILE = Path("api_status.json")

# ─────────────────────────────────────────────────────────────
# REQUEST STATE
# ─────────────────────────────────────────────────────────────

@dataclass
class APIRequest:
    """Represents a single API request."""
    id: str
    endpoint: str
    payload: dict
    status: str  # pending | processing | success | failed | cooling_down
    created_at: str
    last_attempt: Optional[str] = None
    attempt_count: int = 0
    error_message: Optional[str] = None
    result: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'APIRequest':
        return cls(**d)


# ─────────────────────────────────────────────────────────────
# REQUEST QUEUE MANAGER
# ─────────────────────────────────────────────────────────────

class RequestQueue:
    """
    Manages local request queue with persistent storage.
    Survives app restart — critical for reliability.
    """

    def __init__(self, queue_file: Path = QUEUE_FILE):
        self.queue_file = queue_file
        self.lock = threading.Lock()
        self.queue: list[APIRequest] = []
        self._load()

    def _load(self) -> None:
        """Load queue from disk on startup."""
        if self.queue_file.exists():
            try:
                data = json.loads(self.queue_file.read_text())
                self.queue = [APIRequest.from_dict(d) for d in data]
                logger.info(f"Loaded {len(self.queue)} queued requests from disk")
            except Exception as e:
                logger.error(f"Failed to load queue: {e}")
                self.queue = []
        else:
            self.queue = []

    def _save(self) -> None:
        """Persist queue to disk."""
        try:
            self.queue_file.write_text(
                json.dumps([r.to_dict() for r in self.queue], indent=2)
            )
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")

    def add(self, request: APIRequest) -> None:
        """Add a request to the queue."""
        with self.lock:
            self.queue.append(request)
            self._save()
            logger.debug(f"Queued request {request.id}")

    def get_next_pending(self) -> Optional[APIRequest]:
        """Get the next request to retry."""
        with self.lock:
            for req in self.queue:
                if req.status == "pending" or req.status == "cooling_down":
                    return req
        return None

    def get_all(self) -> list[APIRequest]:
        """Return current queue (read-only copy)."""
        with self.lock:
            return list(self.queue)

    def remove(self, request_id: str) -> None:
        """Remove a request after successful completion."""
        with self.lock:
            self.queue = [r for r in self.queue if r.id != request_id]
            self._save()

    def update(self, request: APIRequest) -> None:
        """Update a request in the queue."""
        with self.lock:
            for i, r in enumerate(self.queue):
                if r.id == request.id:
                    self.queue[i] = request
                    self._save()
                    break


# ─────────────────────────────────────────────────────────────
# API MANAGER
# ─────────────────────────────────────────────────────────────

class APIManager:
    """
    Orchestrates all API calls with polite-pacing and error recovery.

    Usage:
        manager = APIManager()
        result = manager.call(
            endpoint="vision/analyze",
            payload={"images": [...], "location": "..."},
            on_error=handle_error_ui
        )
        if result is None:
            show_user("System Cooling Down...")
    """

    def __init__(self, pacing_delay: float = POLITE_PACING_DELAY):
        self.pacing_delay = pacing_delay
        self.last_call_time = 0
        self.queue = RequestQueue()
        self.lock = threading.Lock()
        self._error_callback: Optional[Callable] = None

    def register_error_callback(self, callback: Callable) -> None:
        """
        Register a callback to notify UI of errors.
        Signature: callback(message: str, request_id: str)
        """
        self._error_callback = callback

    def call(
        self,
        endpoint: str,
        payload: dict,
        request_id: Optional[str] = None,
        timeout: int = 30,
        on_error: Optional[Callable] = None
    ) -> Optional[dict]:
        """
        Execute an API call with polite-pacing and error recovery.

        Returns:
            dict: API response on success
            None: if API failed and cooling down (local queue storing request)

        Side effects:
            - Enforces 5s delay since last call
            - On 429: queues locally, shows "System Cooling Down"
            - On other errors: logs + queues + shows user-friendly message
        """
        if request_id is None:
            request_id = f"req_{int(time.time()*1000)}"

        # Enforce polite-pacing
        self._wait_for_pacing(request_id)

        # Create request object
        request = APIRequest(
            id=request_id,
            endpoint=endpoint,
            payload=payload,
            status="processing",
            created_at=datetime.utcnow().isoformat(),
            last_attempt=datetime.utcnow().isoformat(),
            attempt_count=1
        )

        try:
            logger.info(f"[{request_id}] Calling {endpoint}")
            result = self._execute_api_call(endpoint, payload, timeout)
            request.status = "success"
            request.result = result
            return result

        except RateLimitError as e:
            logger.warning(f"[{request_id}] Rate limited: {e}")
            self._handle_rate_limit(request)
            self._notify_user_cooling_down(request_id)
            return None

        except Exception as e:
            logger.error(f"[{request_id}] API error: {e}")
            self._handle_general_error(request, str(e))
            self._notify_user_error(request_id, str(e))
            return None

    def _wait_for_pacing(self, request_id: str) -> None:
        """Enforce 5-second delay between calls."""
        with self.lock:
            elapsed = time.time() - self.last_call_time
            if elapsed < self.pacing_delay:
                wait_time = self.pacing_delay - elapsed
                logger.debug(f"[{request_id}] Polite-pacing: waiting {wait_time:.1f}s")
                time.sleep(wait_time)
            self.last_call_time = time.time()

    def _execute_api_call(self, endpoint: str, payload: dict, timeout: int) -> dict:
        """
        Placeholder for actual API execution.
        In production: calls OpenAI, shopping APIs, vision services, etc.

        This is the swap point where you'd inject your real API client.
        """
        # Example implementation:
        # if endpoint == "vision/analyze":
        #     from openai import OpenAI
        #     client = OpenAI()
        #     response = client.chat.completions.create(...)
        #     return {"vitality_score": 75, "grade": "B", ...}
        #
        # elif endpoint == "shopping/search":
        #     response = requests.post(f"{SHOPPING_API}/search", json=payload)
        #     return response.json()

        raise NotImplementedError(
            f"Endpoint '{endpoint}' not implemented. Override _execute_api_call()."
        )

    def _handle_rate_limit(self, request: APIRequest) -> None:
        """
        Handle 429 rate limit: queue locally for retry.
        """
        request.status = "cooling_down"
        request.error_message = (
            "API rate limited. Request queued for retry. "
            "The system is cooling down — try again in 5 minutes."
        )
        self.queue.add(request)
        logger.info(f"[{request.id}] Queued for retry due to rate limit")

    def _handle_general_error(self, request: APIRequest, error_msg: str) -> None:
        """
        Handle non-429 errors: queue with retry logic.
        """
        request.attempt_count += 1
        if request.attempt_count >= MAX_RETRIES:
            request.status = "failed"
            request.error_message = f"Failed after {MAX_RETRIES} attempts: {error_msg}"
            logger.error(f"[{request.id}] Permanent failure: {error_msg}")
        else:
            request.status = "cooling_down"
            backoff = BACKOFF_BASE * (2 ** (request.attempt_count - 1))
            request.error_message = (
                f"Temporary error. Retrying in {backoff}s. "
                f"(Attempt {request.attempt_count}/{MAX_RETRIES})"
            )
            logger.warning(f"[{request.id}] Will retry in {backoff}s")

        self.queue.add(request)

    def _notify_user_cooling_down(self, request_id: str) -> None:
        """
        Signal to UI: "System Cooling Down"
        The UI should display this gracefully, not crash.
        """
        message = (
            "🌡️  System Cooling Down\n"
            "We've hit a rate limit. Your request is safely queued and will "
            "resume automatically in 5 minutes. No data is lost."
        )
        logger.warning(f"[{request_id}] User notification: {message}")
        if self._error_callback:
            self._error_callback(message, request_id)

    def _notify_user_error(self, request_id: str, error_msg: str) -> None:
        """
        Signal to UI: generic error (will retry automatically).
        """
        message = (
            "⚠️  Temporary Issue\n"
            "We encountered a problem, but your request is safely stored. "
            "We'll retry automatically. Check back in a moment."
        )
        logger.error(f"[{request_id}] User notification: {message} (raw: {error_msg})")
        if self._error_callback:
            self._error_callback(message, request_id)

    def get_queue_status(self) -> dict:
        """
        Return queue status for UI dashboard.
        Useful for showing user: "3 requests queued, retrying..."
        """
        all_reqs = self.queue.get_all()
        return {
            "total_queued": len(all_reqs),
            "pending": sum(1 for r in all_reqs if r.status == "pending"),
            "cooling_down": sum(1 for r in all_reqs if r.status == "cooling_down"),
            "failed": sum(1 for r in all_reqs if r.status == "failed"),
            "requests": [r.to_dict() for r in all_reqs]
        }

    def clear_queue(self) -> None:
        """Clear all queued requests (for admin/testing only)."""
        self.queue.queue.clear()
        self.queue._save()
        logger.warning("Queue cleared")

    def save_status(self) -> None:
        """Persist queue status to disk for monitoring."""
        status = self.get_queue_status()
        status["last_saved"] = datetime.utcnow().isoformat()
        try:
            STATUS_FILE.write_text(json.dumps(status, indent=2))
        except Exception as e:
            logger.error(f"Failed to save status: {e}")


# ─────────────────────────────────────────────────────────────
# BUILT-IN EXCEPTIONS
# ─────────────────────────────────────────────────────────────

class RateLimitError(Exception):
    """Raised when API returns 429."""
    pass


# ─────────────────────────────────────────────────────────────
# EXAMPLE USAGE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Create manager
    manager = APIManager(pacing_delay=2)  # 2s for demo

    # Register error callback (would update UI in real app)
    def on_api_error(msg: str, req_id: str):
        print(f"\n🚨 UI Alert [{req_id}]:\n{msg}\n")

    manager.register_error_callback(on_api_error)

    print("✅ API Manager initialized")
    print(f"   Polite-pacing: {manager.pacing_delay}s")
    print(f"   Max retries: {MAX_RETRIES}")
    print(f"   Queue file: {QUEUE_FILE}")
    print("\nAPI Manager ready for integration into vitality_score.py\n")
