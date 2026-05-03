# Asynchronous Job Queue Architecture

## Overview

Design Diagnosis now uses **Redis + RQ (Redis Queue)** for asynchronous background job processing. This solves the critical problem of browser timeout (504 Gateway Timeout) when Premium Tier vision analysis exceeds 60 seconds.

## Problem Solved

### Before (Synchronous)
```
User clicks "Pay" → Browser waits for response → Vision AI runs (60+ seconds) → 504 Timeout
```

**Issues**:
- Browser timeout after 60 seconds (nginx default)
- User sees blank error page
- Report never generated
- Email never sent
- Bad user experience

### After (Asynchronous)
```
User clicks "Pay" → Instant response (202 Accepted) → Vision AI runs in background → Email delivered
```

**Benefits**:
- Instant success page shown to user
- Heavy analysis runs in background worker
- No timeout issues (workers can run 10+ minutes)
- Email with PDF sent when complete
- Professional, scalable architecture

## Architecture Components

### 1. Redis
- In-memory data store
- Manages job queue and job state
- Persists job results (24 hours)
- Minimal configuration needed

### 2. RQ (Redis Queue)
- Simple, lightweight job queue library
- Python-native (no Celery complexity)
- Job status tracking
- Automatic retries on failure

### 3. Queue Manager (`queue_manager.py`)
- Provides `enqueue_premium_analysis()` function
- Manages Redis connection pooling
- Job status API
- Health checks

### 4. Background Tasks (`background_tasks.py`)
- `run_premium_vision_analysis()` - Main worker task
- `generate_vitality_report_pdf()` - Report generation
- `send_premium_report_email()` - Email delivery

### 5. Worker Process (`worker.py`)
- Standalone Python process
- Polls Redis queue
- Executes jobs sequentially
- Automatic error handling and retries

## Data Flow

### Premium Tier Payment Success

```
1. User completes Stripe payment
   └─> Payment webhook triggers /payment-success

2. /payment-success endpoint:
   └─> Mark payment as "completed" in database
   └─> Get submission + image URLs
   └─> ENQUEUE job: run_premium_vision_analysis()
   └─> Return: 200 OK + success.html (instant!)
   └─> User sees: "Payment successful! Rachel's AI is analyzing..."

3. Redis Queue (background):
   └─> Job sits in queue (usually <1 second)

4. RQ Worker (separate process):
   └─> Pick up job from queue
   └─> Run Vision AI analysis (60+ seconds, OK!)
   └─> Generate PDF report
   └─> Send email with attachment
   └─> Mark submission as "completed"
   └─> Job status → "finished"

5. User experience:
   └─> Instant success page
   └─> Email arrives in 2-5 minutes
   └─> PDF report ready to download
```

## Setup Instructions

### Local Development

#### Step 1: Install Redis

**macOS (with Homebrew)**:
```bash
brew install redis
brew services start redis
# Verify: redis-cli ping → "PONG"
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
# Verify: redis-cli ping → "PONG"
```

**Docker**:
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
# This includes: redis>=5.0.0, rq>=1.15.0
```

#### Step 3: Start the Web Server

```bash
# Terminal 1: FastAPI server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 4: Start the Worker

```bash
# Terminal 2: RQ worker (in same directory)
python worker.py

# Or with specific queue:
python worker.py --queues premium_analysis

# Or with custom name:
python worker.py --name my-worker --queues premium_analysis
```

#### Step 5: Monitor Jobs (Optional)

```bash
# Terminal 3: RQ Dashboard (web UI)
pip install rq-dashboard
rq-dashboard -p 9181
# Visit: http://localhost:9181
```

## Production Deployment

### Environment Variables

Add to `.env` or deployment configuration:

```bash
# Redis Configuration
REDIS_HOST=redis.example.com        # Your Redis server
REDIS_PORT=6379                     # Redis port (default 6379)
REDIS_DB=0                          # Redis database (default 0)

# Job Configuration
RQ_JOB_TIMEOUT=600                  # Job timeout in seconds (10 minutes)

# Worker Configuration
RQ_WORKER_PROCESSES=4               # Number of worker processes
```

### Docker Deployment

#### docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      redis:
        condition: service_healthy
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
    command: python -m uvicorn main:app --host 0.0.0.0 --port 8000

  worker:
    build: .
    depends_on:
      redis:
        condition: service_healthy
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
    command: python worker.py --queues default premium_analysis

volumes:
  redis-data:
```

**Deploy**:
```bash
docker-compose up -d
```

### Systemd Service (VPS Deployment)

#### /etc/systemd/system/design-diagnosis-worker.service

```ini
[Unit]
Description=Design Diagnosis RQ Worker
After=redis.service
Requires=redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/design-diagnosis-app
Environment="PATH=/var/www/design-diagnosis-app/venv/bin"
ExecStart=/var/www/design-diagnosis-app/venv/bin/python worker.py --queues default premium_analysis
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable**:
```bash
sudo systemctl enable design-diagnosis-worker
sudo systemctl start design-diagnosis-worker
sudo systemctl status design-diagnosis-worker
```

### Monitoring & Logging

#### Check Worker Status
```bash
# Via Redis CLI
redis-cli
> LLEN rq:queue:premium_analysis        # Queue length
> LLEN rq:queue:failed                  # Failed jobs

# Via Python
from rq.job import Job
from redis import Redis
redis_conn = Redis()
job_ids = redis_conn.lrange('rq:jobs:finished', 0, -1)
```

#### View Logs
```bash
# Web server logs
tail -f /var/log/design-diagnosis/web.log

# Worker logs
tail -f /var/log/design-diagnosis/worker.log

# Redis logs
tail -f /var/log/redis/redis-server.log
```

#### Alert on Worker Failures
Monitor these Redis keys:
- `rq:queue:premium_analysis` - Job queue length (should be 0-2)
- `rq:queue:failed` - Failed jobs (should be 0)
- `rq:workers` - Active workers (should be ≥1)

## Code Usage

### Enqueue a Premium Analysis Job

```python
from queue_manager import enqueue_premium_analysis

job_id = enqueue_premium_analysis(
    submission_id=123,
    image_urls=['data:image/jpeg;base64,...', ...],
    user_email='user@example.com',
    property_name='Waterfront Condo',
    job_timeout=600
)

print(f"Job queued: {job_id}")
```

### Check Job Status

```python
from queue_manager import get_job_status

status = get_job_status(job_id)
print(status)
# {
#   "job_id": "...",
#   "status": "queued|started|finished|failed",
#   "created_at": "2026-05-03T...",
#   "progress": 0-100,
#   "result": {...} or "error": "..."
# }
```

### Cancel a Job

```python
from queue_manager import cancel_job

success = cancel_job(job_id)
```

## Error Handling

### What if Redis is Down?

The application has a **graceful fallback**:

1. `enqueue_premium_analysis()` returns `None`
2. Payment success route detects failure
3. Falls back to synchronous analysis (old behavior)
4. User still gets report (just slower)
5. No hard failure

### What if a Worker Dies?

- Job stays in queue
- Another worker picks it up when it restarts
- RQ handles automatic retries

### What if Job Fails?

- RQ stores job in `failed` queue
- Error logged with full traceback
- Admin can retry via dashboard
- User notified via email (optional)

## Scaling

### Single Worker (Development)
- Processes 1 job at a time
- Sufficient for testing

### Multiple Workers (Production)

**Terminal 1**: `python worker.py --name worker-1 --queues default premium_analysis`  
**Terminal 2**: `python worker.py --name worker-2 --queues default premium_analysis`  
**Terminal 3**: `python worker.py --name worker-3 --queues default premium_analysis`  

Each worker processes jobs independently. Redis coordinates job distribution.

**Benefits**:
- 3 concurrent jobs
- If one worker dies, others continue
- Easy horizontal scaling

### With Load Balancer

```
Nginx (load balancer)
  ├─ FastAPI Server 1
  ├─ FastAPI Server 2
  └─ FastAPI Server 3
        ↓
       Redis (shared)
        ↑
  ├─ RQ Worker 1
  ├─ RQ Worker 2
  └─ RQ Worker 3
```

All servers and workers connect to the same Redis instance.

## Troubleshooting

### "Connection refused: 127.0.0.1:6379"

**Cause**: Redis not running

**Fix**:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not, start it:
redis-server &
# Or (macOS): brew services start redis
```

### "Job timeout exceeded"

**Cause**: Vision AI analysis took longer than timeout

**Fix**:
```bash
# Increase timeout in .env
RQ_JOB_TIMEOUT=900  # 15 minutes instead of 10

# Or adjust at enqueue time:
job_id = enqueue_premium_analysis(..., job_timeout=900)
```

### "Worker not processing jobs"

**Cause**: Worker crashed or not watching queue

**Fix**:
```bash
# Check worker is running
ps aux | grep worker.py

# Restart if needed
python worker.py --queues premium_analysis

# Check Redis connectivity
redis-cli ping
```

### "Jobs stuck in queue"

**Cause**: Worker died while processing

**Fix**:
```bash
# Delete stuck job
redis-cli
> DEL rq:job:{job_id}
> LREM rq:queue:premium_analysis 0 {job_id}

# Restart worker
python worker.py --queues premium_analysis
```

## Performance Expectations

### Timing

| Task | Time |
|------|------|
| User payment → Success page | <100ms |
| Job queued | <1 second |
| Vision AI analysis | 60-120 seconds |
| PDF generation | 5-10 seconds |
| Email delivery | 10-30 seconds |
| **Total user-facing wait** | **~2-3 minutes** |

### Scalability

| Workers | Concurrent Jobs | Jobs/Hour |
|---------|-----------------|-----------|
| 1 | 1 | 60 |
| 3 | 3 | 180 |
| 10 | 10 | 600 |

At 10 workers: Can process 600 premium reports per hour (1 per 6 seconds average).

## Security Considerations

### Redis Security
- **Development**: Localhost is fine
- **Production**: Use Redis over TLS with password
  ```python
  redis.Redis(
      host='redis.prod.com',
      port=6380,
      password='your-secure-password',
      ssl=True,
      ssl_cert_reqs='required'
  )
  ```

### Job Data
- Images are encoded in job (in Redis)
- Use Redis persistence (`appendonly yes`)
- Backup Redis regularly
- Clear completed jobs periodically

### Worker Isolation
- Run workers as separate system user (not root)
- Use systemd sandboxing
- Monitor worker processes

## Files Modified/Created

**New Files**:
- `queue_manager.py` - Queue management API
- `background_tasks.py` - Worker task implementations
- `worker.py` - Worker startup script
- `ASYNC_ARCHITECTURE.md` - This documentation

**Modified Files**:
- `main.py` - Payment success route uses queue
- `requirements.txt` - Added redis, rq

**No changes to**:
- Database schema
- Frontend/HTML
- Vision analysis logic
- Email configuration

## Next Steps

1. ✅ Install Redis
2. ✅ Start web server + worker
3. ✅ Test payment flow
4. ✅ Monitor queue dashboard (optional)
5. ✅ Deploy to production
6. ✅ Setup monitoring/alerts

## Support

For issues, check:
1. Redis is running: `redis-cli ping`
2. Worker is running: `ps aux | grep worker.py`
3. Logs: `tail -f /var/log/design-diagnosis/*.log`
4. Queue dashboard: `rq-dashboard`
