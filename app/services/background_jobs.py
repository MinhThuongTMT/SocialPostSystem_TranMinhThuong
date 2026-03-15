"""
Background Jobs Service using APScheduler
Handles scheduled tasks like cleanup, notifications, etc.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from typing import Optional
import logging
from ..config.database import get_database
from ..config.redis_config import get_redis
from pytz import utc

logger = logging.getLogger(__name__)


class BackgroundJobsService:
    """
    Service for managing background jobs and scheduled tasks
    """
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running = False
    
    def initialize(self):
        """Initialize the scheduler"""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler(timezone=utc)
            logger.info("✅ Background Jobs Scheduler initialized")
    
    def start(self):
        """Start the scheduler and register jobs"""
        if self.scheduler:
            self.scheduler.start()
            self.is_running = True
            logger.info("🚀 Background Jobs Scheduler started")
            
            # Register scheduled jobs
            self._register_jobs()
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("🛑 Background Jobs Scheduler stopped")
    
    def _register_jobs(self):
        """Register all background jobs"""
        # Cleanup old audit logs every hour
        self.scheduler.add_job(
            self.cleanup_old_audit_logs,
            "interval",
            hours=1,
            id="cleanup_audit_logs"
        )
        
        # Generate daily statistics every day at midnight
        self.scheduler.add_job(
            self.generate_daily_statistics,
            "cron",
            hour=0,
            minute=0,
            id="daily_statistics"
        )
        
        # Clear expired cache keys every 30 minutes
        self.scheduler.add_job(
            self.cleanup_expired_cache,
            "interval",
            minutes=30,
            id="cleanup_cache"
        )
        
        # Send notification emails every hour
        self.scheduler.add_job(
            self.process_pending_notifications,
            "interval",
            minutes=5,
            id="process_notifications"
        )
        
        logger.info("📋 All background jobs registered")
    
    async def cleanup_old_audit_logs(self):
        """
        Clean up audit logs older than 30 days
        Runs hourly
        """
        try:
            db = get_database()  # NOT async - returns database instance directly
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = await db.audit_logs.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 Cleaned {result.deleted_count} old audit logs")
                
                # Log this cleanup action
                await db.audit_logs.insert_one({
                    "user_id": "SYSTEM",
                    "resource_type": "audit_logs",
                    "action": "cleanup",
                    "details": f"Deleted {result.deleted_count} logs older than 30 days",
                    "timestamp": datetime.utcnow()
                })
        except Exception as e:
            logger.error(f"❌ Cleanup audit logs error: {str(e)}")
    
    async def generate_daily_statistics(self):
        """
        Generate daily statistics and summaries
        Runs at midnight UTC
        """
        try:
            db = get_database()  # NOT async - returns database instance directly
            
            # Get stats for today
            today = datetime.utcnow().date()
            
            # Count new users today
            new_users = await db.users.count_documents({
                "created_at": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(today, datetime.max.time())
                }
            })
            
            # Count new posts today
            new_posts = await db.posts.count_documents({
                "created_at": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(today, datetime.max.time())
                }
            })
            
            # Store statistics
            redis = await get_redis()
            stats_key = f"daily_stats:{today}"
            
            stats = {
                "date": str(today),
                "new_users": new_users,
                "new_posts": new_posts,
                "total_users": await db.users.count_documents({}),
                "total_posts": await db.posts.count_documents({}),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await redis.setex(stats_key, 86400, str(stats))  # Store for 24 hours
            
            logger.info(f"📊 Daily statistics generated: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Generate statistics error: {str(e)}")
    
    async def cleanup_expired_cache(self):
        """
        Clean up expired cache keys
        Runs every 30 minutes
        """
        try:
            redis = await get_redis()
            
            # Get all cache keys
            pattern = "post:*"
            keys = await redis.keys(pattern)
            
            # Check TTL and log expired ones
            expired_count = 0
            for key in keys:
                ttl = await redis.ttl(key)
                # Redis returns -2 for missing keys, -1 for keys with no expiry
                if ttl == -2:
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"🗑️  Found {expired_count} expired cache entries")
                
        except Exception as e:
            logger.error(f"❌ Cleanup cache error: {str(e)}")
    
    async def process_pending_notifications(self):
        """
        Process pending notifications and send emails
        Runs every 5 minutes
        
        In production: integrate with email service (SendGrid, AWS SES, etc.)
        """
        try:
            redis = await get_redis()
            
            # Get pending notifications queue
            pending = await redis.lrange("notifications:pending", 0, -1)
            
            if pending:
                logger.info(f"📧 Processing {len(pending)} pending notifications")
                
                # Example: Send email or push notification
                for notification in pending[:10]:  # Process first 10
                    try:
                        # In production: call email service here
                        # await send_email(notification)
                        
                        # Remove from queue
                        await redis.lpop("notifications:pending")
                        logger.debug(f"✅ Notification processed")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to process notification: {str(e)}")
                
        except Exception as e:
            logger.error(f"❌ Process notifications error: {str(e)}")
    
    async def send_email_notification(self, email: str, subject: str, body: str):
        """
        Queue email notification to be sent asynchronously
        
        Args:
            email: Recipient email
            subject: Email subject
            body: Email body
        
        In production: integrate with real email service
        """
        try:
            redis = await get_redis()  # CORRECT async call to get Redis connection
            
            notification = {
                "email": email,
                "subject": subject,
                "body": body,
                "created_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            # Queue notification
            await redis.rpush("notifications:pending", str(notification))
            logger.info(f"📬 Notification queued for {email}")
            
        except Exception as e:
            logger.error(f"❌ Queue notification error: {str(e)}")
    
    async def log_background_activity(self, job_name: str, status: str, details: str = ""):
        """Log background job execution"""
        try:
            db = get_database()  # NOT async - returns database instance directly
            
            await db.background_jobs_log.insert_one({
                "job_name": job_name,
                "status": status,
                "details": details,
                "executed_at": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"❌ Log background activity error: {str(e)}")


# Singleton instance
background_jobs_service = BackgroundJobsService()
