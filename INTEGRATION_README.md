# Integration Layer — Polite-Pacing & Error Handling

## Overview

Three new modules handle API resilience:

1. **api_manager.py** — Enforces 5s delays between calls, queues failed requests locally
2. **vitality_integration.py** — Wires APIManager into vitality_score.py
3. **EXPERIENCE_LOGIC.md** & **SHOPPING_LISTS.md** — Reference documents for design principles

## Problem Statement

**The Issue:**
- Users hit rate limits (429 errors) → app crashes or shows raw API errors
- No request persistence → loss of work on network/timeout failures
- Rapid retries aggravate rate limits instead of solving them

**The Solution:**
- 5-second mandatory delay between all API calls ("polite-pacing")
- Local queue persists failed requests to disk (survives app restart)
- User sees "System Cooling Down" instead of crash
- Background retry logic with exponential backoff (5s, 10s, 20s, 40s)

---

## Architecture

```
┌─────────────┐
│    UI       │ (React, web, etc.)
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────┐
│  vitality_integration.py            │
│  analyse_listing_managed()          │
│  - Error recovery                   │
│  - Status reporting                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│  api_manager.py                    │
│  APIManager + RequestQueue         │
│  - Polite-pacing (5s delay)        │
│  - Local persistence               │
│  - Retry logic                     │
└──────┬───────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│  OpenAI / Shopping APIs            │
│  (Real external services)          │
└────────────────────────────────────┘
```

---

## Files

### api_manager.py
Low-level API orchestration. Handles:
- **RequestQueue**: Persistent local queue (JSON on disk)
- **APIManager**: Polite-pacing + retry logic
- **APIRequest**: State machine for individual requests

**Key classes:**
```python
class APIRequest:
    id: str                 # Unique ID
    endpoint: str           # "vision/analyze", "shopping/search", etc.
    payload: dict           # Request body
    status: str             # pending | processing | success | failed | cooling_down
    created_at: str
    attempt_count: int      # Tracks retries
    error_message: str
    result: dict           # Response on success

class APIManager:
    # Enforces polite-pacing (5s between calls)
    call(endpoint, payload, request_id=None) -> dict or None
    
    # Local queue survives app restart
    get_queue_status() -> {total_queued, pending, cooling_down, failed}
```

### vitality_integration.py
High-level wrapper. Drop-in replacements for vitality_score.py:

```python
# ORIGINAL:
report = analyse_listing(images, location, budget)

# WITH MANAGED ERROR HANDLING:
report = analyse_listing_managed(images, location, budget)

# If rate-limited:
# report = {
#     "status": "cooling_down",
#     "message": "🌡️  System Cooling Down...",
#     "vitality_score": None,
#     "grade": None
# }
```

---

## Integration Steps

### 1. Import the Manager (In Your App Entry Point)

```python
from vitality_integration import (
    analyse_listing_managed,
    get_queue_status,
    retry_failed_requests,
    SYSTEM_COOLING_DOWN,
    SYSTEM_ERROR
)

# Initialize (one-time)
from api_manager import APIManager
manager = APIManager(pacing_delay=5)
```

### 2. Replace Your analyse_listing() Call

**Before:**
```python
report = analyse_listing(
    image_paths=images,
    location="Ampang, Malaysia",
    budget=1500,
    currency="RM"
)
```

**After:**
```python
def on_cooling_down():
    """Callback if API hits rate limit."""
    ui.show_banner("System Cooling Down — will retry in 5 minutes")

report = analyse_listing_managed(
    image_paths=images,
    location="Ampang, Malaysia",
    budget=1500,
    currency="RM",
    on_cooling_down=on_cooling_down
)

# Check status
if report["status"] == "cooling_down":
    ui.show_message(report["message"])
    # Request is queued — user doesn't need to retry manually
elif report["status"] == "error":
    ui.show_message(report["message"])
else:
    ui.display_vitality_report(report)  # Success
```

### 3. Implement Real API Calls

The integration layer is currently a skeleton. You must implement:

**In api_manager.py**, override `_execute_api_call()`:
```python
def _execute_api_call(self, endpoint: str, payload: dict, timeout: int) -> dict:
    if endpoint == "vitality/analyze":
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=payload["messages"],
            max_tokens=payload.get("max_tokens", 3000),
            response_format={"type": "json_object"}
        )
        return {"content": response.choices[0].message.content}
    
    elif endpoint == "shopping/search":
        # Your shopping API here
        pass
    
    # ... more endpoints
```

**In vitality_integration.py**, override `_execute_managed_api()`:
```python
def _execute_managed_api(messages, max_tokens, label, request_id) -> str:
    from openai import OpenAI, RateLimitError
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=max_tokens,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content
```

### 4. UI Integration

Display queue status on a dashboard:
```python
# Get queue status
status = get_queue_status()
# {
#     "total_queued": 3,
#     "pending": 1,
#     "cooling_down": 2,
#     "failed": 0,
#     "requests": [...]
# }

# Show to user:
if status["total_queued"] > 0:
    ui.show_banner(
        f"⏳ {status['cooling_down']} request(s) in queue. "
        f"Retrying automatically."
    )
```

**Manual retry button (admin/advanced):**
```python
def on_retry_button_clicked():
    results = retry_failed_requests()
    # {success: 2, failed: 0, cooling_down: 1}
    ui.show_message(
        f"✅ {results['success']} recovered\n"
        f"⏳ {results['cooling_down']} still cooling down\n"
        f"❌ {results['failed']} permanent failures"
    )
```

---

## Error States

### State 1: Success
```json
{
  "status": "success",
  "vitality_score": 72,
  "grade": "B",
  "summary": "...good listing...",
  "dimensions": {...},
  "shopping_list": [...]
}
```

### State 2: Rate Limited (System Cooling Down)
```json
{
  "status": "cooling_down",
  "message": "🌡️  System Cooling Down\nWe've hit a rate limit. Your request is safely queued...",
  "user_action": "wait_and_retry",
  "vitality_score": null,
  "grade": null,
  "summary": "Analysis paused due to API rate limit. Please try again shortly."
}
```
**User experience:** Banner appears. Request is queued. Retry happens automatically in 5 minutes.

### State 3: Temporary Error
```json
{
  "status": "error",
  "message": "⚠️  System Temporary Error\nWe encountered an issue, but your request is safely stored...",
  "user_action": "wait_and_retry",
  "vitality_score": null,
  "grade": null
}
```
**User experience:** Banner appears. Request is queued. Retries happen with exponential backoff.

---

## Local Persistence

Failed requests are saved to `api_request_queue.json`:

```json
[
  {
    "id": "req_1704067200123",
    "endpoint": "vitality/analyze",
    "payload": {...},
    "status": "cooling_down",
    "created_at": "2024-01-01T12:00:00",
    "last_attempt": "2024-01-01T12:05:00",
    "attempt_count": 1,
    "error_message": "Rate limit hit",
    "result": null
  }
]
```

**Benefits:**
- If app crashes, queue survives → requests don't get lost
- On restart, app can resume retrying
- Admin can inspect failed requests for debugging

---

## Polite-Pacing Logic

5-second delay enforced between **all** API calls:

```
Call 1: t=0s  ✅
         ↓ (wait 5s)
Call 2: t=5s  ✅
         ↓ (wait 5s)
Call 3: t=10s ✅
```

This prevents:
- Overwhelming the API server
- Triggering rate limits
- User seeing "too many requests" errors

**Configurable:** `APIManager(pacing_delay=5)` (default 5 seconds)

---

## Exponential Backoff

For non-rate-limit errors, retries are spaced with exponential backoff:

```
Attempt 1: Fails immediately
Attempt 2: Retry after 5s
Attempt 3: Retry after 10s (5 * 2^1)
Attempt 4: Retry after 20s (5 * 2^2)
Attempt 5: Permanent failure (max 4 retries)
```

---

## Testing

### Test 1: Simulate Rate Limit
```python
from api_manager import APIManager, RateLimitError

manager = APIManager()

# Mock a rate limit error:
# (In real app, OpenAI would raise this)
result = manager.call(
    endpoint="test",
    payload={"msg": "hi"}
)
# Returns: None (request queued)

status = manager.get_queue_status()
# {total_queued: 1, pending: 0, cooling_down: 1, failed: 0}
```

### Test 2: Queue Persistence
```python
# Save to disk
manager.save_status()

# Read from disk
import json
data = json.load(open("api_status.json"))
print(data["cooling_down"])  # 1
```

### Test 3: Polite-Pacing Timing
```python
import time
manager = APIManager(pacing_delay=2)

start = time.time()
# Call 1
# Call 2 (will wait ~2s)
elapsed = time.time() - start
assert elapsed >= 2, "Pacing not enforced!"
```

---

## Reference Documents

### EXPERIENCE_LOGIC.md
Documents the "Stager's Logic" framework:
- Colour Coherence scoring
- Functional Anchors (bedside tables, workspace, etc.)
- Staging Integrity (what to show vs. what to mention)
- Reality Gap categories
- Listing type weights

### SHOPPING_LISTS.md
Documents shopping recommendations:
- Budget tiers (Value / Signature / Luxury)
- Regional vendors (SE Asia, Europe, North America, Australia)
- Item sourcing logic (online vs. in-store)
- "Why" justifications for each item
- Show-It list (items that exist but aren't photographed)

---

## Troubleshooting

### "System Cooling Down" appears frequently
**Cause:** Rate limit is being hit.  
**Fix:**
1. Increase `pacing_delay` from 5s to 10s
2. Reduce batch size (fewer images per request)
3. Check OpenAI usage dashboard for other clients

### Requests stuck in "cooling_down" state
**Cause:** 5-minute cooldown hasn't elapsed.  
**Fix:**
1. Wait 5 minutes, or
2. Admin click "Retry Now" button (force early retry)

### Queue not persisting across restarts
**Cause:** `api_request_queue.json` is being deleted or path is wrong.  
**Fix:**
1. Check queue file path: `print(QUEUE_FILE)`
2. Ensure app has write permissions in that directory
3. Check logs for save errors

### App still showing raw API errors
**Cause:** Not using `analyse_listing_managed()`.  
**Fix:**
```python
# ❌ Wrong (old way)
report = analyse_listing(...)

# ✅ Right (error-safe)
report = analyse_listing_managed(...)
```

---

## Next Steps

1. **Implement real API calls** in `_execute_api_call()` and `_execute_managed_api()`
2. **Wire into your frontend** — replace `analyse_listing()` with `analyse_listing_managed()`
3. **Add UI banners** for "System Cooling Down" and queue status
4. **Test with real Airbnb photos** to verify end-to-end flow
5. **Monitor queue** in production — if high backlog, increase pacing delay

---

## API Reference

### APIManager

```python
manager = APIManager(pacing_delay=5)

# Make a call (polite-paced, auto-queuing on error)
result = manager.call(
    endpoint="vitality/analyze",
    payload={"images": [...], "location": "..."},
    request_id="req_123"  # optional
)
# Returns: dict on success, None on error (queued)

# Get queue status
status = manager.get_queue_status()
# {total_queued, pending, cooling_down, failed, requests}

# Admin: force retry of all queued requests
results = retry_failed_requests()
# {success, failed, cooling_down}

# Admin: clear queue (testing only!)
manager.clear_queue()

# Persist queue to disk
manager.save_status()

# Register error callback (UI notification)
manager.register_error_callback(
    lambda msg, req_id: ui.show_banner(msg)
)
```

### vitality_integration

```python
# Wrapped analyse_listing with error recovery
report = analyse_listing_managed(
    image_paths=[...],
    location="Ampang, Malaysia",
    budget=1500,
    currency="RM",
    on_cooling_down=lambda: ui.show_cooling_banner()
)
# Returns: dict with status field

# Get queue status
status = get_queue_status()

# Manually trigger retry
results = retry_failed_requests()
```

---

## Philosophy

> "The app should never crash. The user should never see a raw API error."

Every failure is recoverable. Every request is persistent. The UI always has something meaningful to tell the user.
