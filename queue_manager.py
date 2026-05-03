"""
Asynchronous Job Queue Manager
Handles background processing for Premium Tier Vision Analysis

Uses Redis + RQ (Redis Queue) for lightweight, production-ready job queuing.
"""

import redis
import logging
from rq import Queue, Worker
from rq.job import JobStatus
from datetime import timedelta
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

# Redis connection pool (reusable across workers)
redis_conn = None

def get_redis_connection():
    """Get or create Redis connection"""
    global redis_conn
    if redis_conn is None:
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        redis_db = int(os.environ.get('REDIS_DB', 0))
        
        try:
            redis_conn = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 3   # TCP_KEEPCNT
                }
            )
            # Test connection
            redis_conn.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            redis_conn = None
    return redis_conn

def get_queue(name: str = 'default') -> Optional[Queue]:
    """Get or create an RQ queue"""
    try:
        conn = get_redis_connection()
        if conn is None:
            logger.warning("⚠️  Redis not available, queue operations disabled")
            return None
        return Queue(name, connection=conn)
    except Exception as e:
        logger.error(f"❌ Failed to get queue: {e}")
        return None

def enqueue_premium_analysis(
    submission_id: int,
    image_urls: list,
    user_email: str,
    property_name: str,
    job_timeout: int = 600  # 10 minutes
) -> Optional[str]:
    """
    Queue a Premium Tier analysis job
    
    Args:
        submission_id: Database submission ID
        image_urls: List of image URLs to analyze
        user_email: Email for report delivery
        property_name: Property name for report
        job_timeout: Job timeout in seconds
    
    Returns:
        Job ID (str) if queued successfully, None if failed
    """
    try:
        queue = get_queue('premium_analysis')
        if queue is None:
            logger.error("❌ Premium analysis queue unavailable")
            return None
        
        # Import here to avoid circular imports
        from background_tasks import run_premium_vision_analysis
        
        job = queue.enqueue(
            run_premium_vision_analysis,
            submission_id=submission_id,
            image_urls=image_urls,
            user_email=user_email,
            property_name=property_name,
            job_timeout=timedelta(seconds=job_timeout),
            result_ttl=86400,  # Keep result for 24 hours
            failure_ttl=3600   # Keep failure for 1 hour
        )
        
        logger.info(f"📤 Queued premium analysis: Job {job.id} for submission {submission_id}")
        return job.id
        
    except Exception as e:
        logger.error(f"❌ Failed to enqueue premium analysis: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get job status and progress
    
    Args:
        job_id: RQ job ID
    
    Returns:
        Dict with status, progress, result, error
    """
    try:
        conn = get_redis_connection()
        if conn is None:
            return {"status": "unavailable", "error": "Redis not connected"}
        
        from rq.job import Job
        job = Job.fetch(job_id, connection=conn)
        
        result = {
            "job_id": job_id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "progress": job.meta.get('progress', 0) if job.meta else 0
        }
        
        # Add result or error
        if job.is_finished:
            result["result"] = job.result
        elif job.is_failed:
            result["error"] = job.exc_info
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get job status: {e}")
        return {"status": "error", "error": str(e)}

def cancel_job(job_id: str) -> bool:
    """Cancel a queued or running job"""
    try:
        conn = get_redis_connection()
        if conn is None:
            return False
        
        from rq.job import Job
        job = Job.fetch(job_id, connection=conn)
        job.cancel()
        logger.info(f"🛑 Cancelled job {job_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to cancel job: {e}")
        return False

def start_worker(queue_names: list = None, worker_name: str = None):
    """
    Start an RQ worker process
    Call this from a separate process/container
    
    Args:
        queue_names: List of queue names to process (default: ['default', 'premium_analysis'])
        worker_name: Worker name for logging
    """
    if queue_names is None:
        queue_names = ['default', 'premium_analysis']
    
    try:
        conn = get_redis_connection()
        if conn is None:
            logger.error("❌ Cannot start worker: Redis not available")
            return
        
        worker = Worker(
            queues=[Queue(q, connection=conn) for q in queue_names],
            connection=conn,
            name=worker_name or 'design-diagnosis-worker',
            default_result_ttl=3600,  # 1 hour
            failure_ttl=3600           # 1 hour
        )
        
        logger.info(f"🚀 RQ Worker started: {worker.name}")
        logger.info(f"📋 Watching queues: {queue_names}")
        
        worker.work(with_scheduler=False)
        
    except Exception as e:
        logger.error(f"❌ Worker failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

def check_redis_health() -> bool:
    """Check if Redis is available and healthy"""
    try:
        conn = get_redis_connection()
        if conn is None:
            return False
        conn.ping()
        return True
    except Exception as e:
        logger.error(f"❌ Redis health check failed: {e}")
        return False
