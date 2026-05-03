#!/usr/bin/env python3
"""
Redis Configuration Fixer
Solves: 200/CHDIR error by fixing redis.conf permissions and settings

This script:
1. Finds and replaces redis.conf settings for systemd compatibility
2. Changes directory settings from /var/lib/redis to /tmp
3. Disables daemonize mode for systemd
4. Reloads systemd daemon
5. Restarts Redis server

Usage:
    sudo python3 fix_redis.py

Requirements:
    - Must run with sudo (requires root privileges)
    - /etc/redis/redis.conf must exist
"""

import os
import re
import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_root():
    """Verify script is running as root"""
    if os.geteuid() != 0:
        logger.error("❌ ERROR: This script must run with sudo")
        logger.error("   Usage: sudo python3 fix_redis.py")
        sys.exit(1)
    logger.info("✅ Running as root")

def backup_config(config_path):
    """Create backup of redis.conf before modifying"""
    backup_path = f"{config_path}.backup"
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        logger.info(f"✅ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None

def fix_redis_conf(config_path):
    """Fix redis.conf settings"""
    logger.info(f"📝 Reading redis.conf: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"❌ Failed to read redis.conf: {e}")
        return False
    
    original_content = content
    changes = []
    
    # Fix 1: Change supervised setting
    # Match "supervised systemd" or "supervised auto" (ignoring comments)
    logger.info("🔧 Fix 1: Setting supervised to 'no'...")
    pattern1 = r'^supervised\s+(systemd|auto|yes)'
    if re.search(pattern1, content, re.MULTILINE | re.IGNORECASE):
        content = re.sub(pattern1, 'supervised no', content, flags=re.MULTILINE | re.IGNORECASE)
        changes.append("✅ supervised → no")
        logger.info("   ✓ Found and replaced 'supervised systemd/auto'")
    else:
        logger.warning("   ⚠️  'supervised' setting not found (may already be correct)")
    
    # Fix 2: Change directory
    # Match "dir /var/lib/redis" and replace with "dir /tmp"
    logger.info("🔧 Fix 2: Setting dir to '/tmp'...")
    pattern2 = r'^dir\s+/var/lib/redis'
    if re.search(pattern2, content, re.MULTILINE | re.IGNORECASE):
        content = re.sub(pattern2, 'dir /tmp', content, flags=re.MULTILINE | re.IGNORECASE)
        changes.append("✅ dir → /tmp")
        logger.info("   ✓ Found and replaced 'dir /var/lib/redis'")
    else:
        logger.warning("   ⚠️  'dir' setting not found (may already be correct)")
    
    # Fix 3: Disable daemonize
    # Match "daemonize yes" and replace with "daemonize no"
    logger.info("🔧 Fix 3: Disabling daemonize...")
    pattern3 = r'^daemonize\s+yes'
    if re.search(pattern3, content, re.MULTILINE | re.IGNORECASE):
        content = re.sub(pattern3, 'daemonize no', content, flags=re.MULTILINE | re.IGNORECASE)
        changes.append("✅ daemonize → no")
        logger.info("   ✓ Found and replaced 'daemonize yes'")
    else:
        logger.warning("   ⚠️  'daemonize' setting not found (may already be correct)")
    
    # Write changes back
    if content != original_content:
        try:
            with open(config_path, 'w') as f:
                f.write(content)
            logger.info(f"✅ redis.conf updated with {len(changes)} changes:")
            for change in changes:
                logger.info(f"   {change}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write redis.conf: {e}")
            return False
    else:
        logger.info("ℹ️  No changes needed (all settings already correct)")
        return True

def reload_systemd():
    """Reload systemd daemon configuration"""
    logger.info("🔄 Reloading systemd daemon...")
    try:
        result = subprocess.run(
            ['systemctl', 'daemon-reload'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("✅ systemd daemon reloaded")
            return True
        else:
            logger.error(f"❌ systemctl daemon-reload failed:")
            logger.error(f"   stdout: {result.stdout}")
            logger.error(f"   stderr: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ systemctl daemon-reload error: {e}")
        return False

def restart_redis():
    """Restart Redis server"""
    logger.info("🔄 Restarting Redis server...")
    try:
        result = subprocess.run(
            ['systemctl', 'restart', 'redis-server'],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            logger.info("✅ Redis server restarted")
            return True
        else:
            logger.error(f"❌ systemctl restart redis-server failed:")
            logger.error(f"   stdout: {result.stdout}")
            logger.error(f"   stderr: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ systemctl restart error: {e}")
        return False

def verify_redis():
    """Verify Redis is running"""
    logger.info("✔️  Verifying Redis status...")
    try:
        result = subprocess.run(
            ['systemctl', 'status', 'redis-server'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("✅ Redis is running and healthy")
            return True
        else:
            logger.warning("⚠️  Redis status check returned non-zero")
            logger.warning(f"   stdout: {result.stdout[:200]}")
            logger.warning(f"   stderr: {result.stderr[:200]}")
            return False
    except Exception as e:
        logger.error(f"❌ Redis verification failed: {e}")
        return False

def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("🚀 REDIS CONFIGURATION FIXER")
    logger.info("=" * 70)
    
    # Step 1: Check root
    check_root()
    
    # Step 2: Define config path
    config_path = '/etc/redis/redis.conf'
    if not os.path.exists(config_path):
        logger.error(f"❌ ERROR: {config_path} not found")
        logger.error("   Is Redis installed? Try: sudo apt install redis-server")
        sys.exit(1)
    
    logger.info(f"📁 Config file: {config_path}")
    
    # Step 3: Backup original
    backup_path = backup_config(config_path)
    if not backup_path:
        logger.error("❌ Backup failed, aborting")
        sys.exit(1)
    
    # Step 4: Fix configuration
    if not fix_redis_conf(config_path):
        logger.error("❌ Configuration fix failed")
        logger.info(f"📁 Backup available at: {backup_path}")
        sys.exit(1)
    
    # Step 5: Reload systemd
    if not reload_systemd():
        logger.warning("⚠️  systemd reload failed (non-critical)")
    
    # Step 6: Restart Redis
    if not restart_redis():
        logger.error("❌ Redis restart failed")
        logger.info(f"📁 Backup available at: {backup_path}")
        logger.info("   Try: sudo cp {backup_path} {config_path}")
        sys.exit(1)
    
    # Step 7: Verify
    if not verify_redis():
        logger.warning("⚠️  Redis verification inconclusive (check manually)")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ REDIS CONFIGURATION FIXED")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Summary of changes:")
    logger.info("  1. supervised → no")
    logger.info("  2. dir → /tmp")
    logger.info("  3. daemonize → no")
    logger.info("")
    logger.info("Redis is now configured for systemd and should work with:")
    logger.info("  python worker.py")
    logger.info("")
    logger.info(f"Backup of original config: {backup_path}")
    logger.info("")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
