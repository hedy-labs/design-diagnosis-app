#!/usr/bin/env python3
"""
RQ Background Worker Startup Script

Runs the asynchronous job queue worker for Premium Tier analysis.
This worker processes long-running Vision AI analysis jobs in the background.

Usage:
    python worker.py                    # Start with default queues
    python worker.py --queues premium_analysis    # Start specific queue
    python worker.py --name worker-1 --queues premium_analysis   # Named worker

Environment Variables:
    REDIS_HOST: Redis server hostname (default: localhost)
    REDIS_PORT: Redis server port (default: 6379)
    REDIS_DB: Redis database number (default: 0)
    RQ_JOB_TIMEOUT: Job timeout in seconds (default: 600)
"""

import sys
import logging
import argparse
from queue_manager import start_worker, check_redis_health

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main worker entry point"""
    parser = argparse.ArgumentParser(description='Design Diagnosis RQ Worker')
    parser.add_argument(
        '--queues',
        nargs='+',
        default=['default', 'premium_analysis'],
        help='Queue names to process (default: default premium_analysis)'
    )
    parser.add_argument(
        '--name',
        default=None,
        help='Worker name for logging (auto-generated if not provided)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("🚀 DESIGN DIAGNOSIS RQ WORKER STARTUP")
    logger.info("=" * 80)
    
    # Check Redis health
    logger.info("🔍 Checking Redis connection...")
    if not check_redis_health():
        logger.error("❌ Redis is not available. Please ensure Redis is running.")
        logger.error("   Install Redis: brew install redis (macOS) or apt install redis (Linux)")
        logger.error("   Start Redis: redis-server")
        sys.exit(1)
    
    logger.info("✅ Redis connection OK")
    logger.info(f"📋 Watching queues: {args.queues}")
    
    if args.name:
        logger.info(f"👷 Worker name: {args.name}")
    
    logger.info("=" * 80)
    logger.info("🟢 Worker online and ready to process jobs")
    logger.info("=" * 80)
    
    # Start worker
    start_worker(queue_names=args.queues, worker_name=args.name)

if __name__ == '__main__':
    main()
