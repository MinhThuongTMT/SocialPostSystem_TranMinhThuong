"""
Event Consumer for Redis Pub/Sub
Implements event-driven architecture for real-time updates
"""
import asyncio
import json
import logging
from typing import Callable, Dict, List
from datetime import datetime
from ..config.redis_config import get_redis
from ..config.database import get_database

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes events from Redis Pub/Sub channels
    Triggered by events like post.created, post.updated, user.followed, etc.
    """
    
    def __init__(self):
        self.is_running = False
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_handlers = {
            "post.created": self.handle_post_created,
            "post.updated": self.handle_post_updated,
            "post.deleted": self.handle_post_deleted,
            "comment.created": self.handle_comment_created,
            "like.created": self.handle_like_created,
            "user.followed": self.handle_user_followed,
        }
    
    async def start(self):
        """Start consuming events from Redis Pub/Sub"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Event Consumer started")
        
        # Start consuming events in background
        asyncio.create_task(self._consume_events())
    
    async def stop(self):
        """Stop consuming events"""
        self.is_running = False
        logger.info("🛑 Event Consumer stopped")
    
    async def _consume_events(self):
        """Main event consumption loop"""
        try:
            redis = await get_redis()
            pubsub = redis.pubsub()
            
            # Subscribe to all event channels
            channels = list(self.event_handlers.keys())
            await pubsub.subscribe(*channels)
            
            logger.info(f"📡 Subscribed to channels: {channels}")
            
            while self.is_running:
                try:
                    # Listen for messages with timeout
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0
                    )
                    
                    if message:
                        await self._handle_event(message)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"❌ Event consumption error: {str(e)}")
                    await asyncio.sleep(1)
            
            await pubsub.unsubscribe(*channels)
            
        except Exception as e:
            logger.error(f"❌ Event consumer error: {str(e)}")
            self.is_running = False
    
    async def _handle_event(self, message: Dict):
        """Route event to appropriate handler"""
        try:
            channel = message.get("channel").decode() if isinstance(message.get("channel"), bytes) else message.get("channel")
            data = message.get("data")
            
            # Parse JSON data
            if isinstance(data, bytes):
                data = data.decode()
            
            try:
                event_data = json.loads(data) if isinstance(data, str) else data
            except json.JSONDecodeError:
                event_data = {"raw": data}
            
            logger.info(f"📥 Event received: {channel} - {event_data}")
            
            # Call appropriate handler
            if channel in self.event_handlers:
                await self.event_handlers[channel](event_data)
            else:
                logger.warning(f"⚠️  No handler for event: {channel}")
                
        except Exception as e:
            logger.error(f"❌ Handle event error: {str(e)}")
    
    # ============ Event Handlers ============
    
    async def handle_post_created(self, event_data: Dict):
        """Handle post.created event"""
        try:
            post_id = event_data.get("post_id")
            user_id = event_data.get("user_id")
            
            logger.info(f"✨ Post created by user {user_id}: {post_id}")
            
            # Update user statistics
            db = await get_database()
            redis = await get_redis()
            
            # Increment user post count
            await redis.incr(f"user_posts_count:{user_id}")
            
            # Log the event
            await db.event_logs.insert_one({
                "event": "post.created",
                "post_id": post_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "processed_at": datetime.utcnow()
            })
            
            logger.info(f"✅ Post created event processed")
            
        except Exception as e:
            logger.error(f"❌ Handle post.created error: {str(e)}")
    
    async def handle_post_updated(self, event_data: Dict):
        """Handle post.updated event"""
        try:
            post_id = event_data.get("post_id")
            user_id = event_data.get("user_id")
            
            logger.info(f"✏️  Post updated: {post_id}")
            
            # Clear post cache
            redis = await self.redis_conn.get_redis()
            await redis.delete(f"post:{post_id}")
            
            db = await get_database()
            await db.event_logs.insert_one({
                "event": "post.updated",
                "post_id": post_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"❌ Handle post.updated error: {str(e)}")
    
    async def handle_post_deleted(self, event_data: Dict):
        """Handle post.deleted event"""
        try:
            post_id = event_data.get("post_id")
            user_id = event_data.get("user_id")
            
            logger.info(f"🗑️  Post deleted: {post_id}")
            
            # Clear post cache
            redis = await get_redis()
            await redis.delete(f"post:{post_id}")
            
            # Decrement user post count
            await redis.decr(f"user_posts_count:{user_id}")
            
            db = await get_database()
            await db.event_logs.insert_one({
                "event": "post.deleted",
                "post_id": post_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"❌ Handle post.deleted error: {str(e)}")
    
    async def handle_comment_created(self, event_data: Dict):
        """Handle comment.created event"""
        try:
            comment_id = event_data.get("comment_id")
            post_id = event_data.get("post_id")
            user_id = event_data.get("user_id")
            
            logger.info(f"💬 Comment created on post {post_id}: {comment_id}")
            
            # Invalidate post cache
            redis = await get_redis()
            await redis.delete(f"post:{post_id}")
            
            db = await get_database()
            await db.event_logs.insert_one({
                "event": "comment.created",
                "comment_id": comment_id,
                "post_id": post_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"❌ Handle comment.created error: {str(e)}")
    
    async def handle_like_created(self, event_data: Dict):
        """Handle like.created event"""
        try:
            post_id = event_data.get("post_id")
            user_id = event_data.get("user_id")
            
            logger.info(f"❤️  Post {post_id} liked by user {user_id}")
            
            # Update like count in cache
            redis = await get_redis()
            await redis.incr(f"post_likes:{post_id}")
            
            # Invalidate post cache
            await redis.delete(f"post:{post_id}")
            
            db = await get_database()
            await db.event_logs.insert_one({
                "event": "like.created",
                "post_id": post_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"❌ Handle like.created error: {str(e)}")
    
    async def handle_user_followed(self, event_data: Dict):
        """Handle user.followed event"""
        try:
            follower_id = event_data.get("follower_id")
            following_id = event_data.get("following_id")
            
            logger.info(f"👥 User {follower_id} followed {following_id}")
            
            # Update follower/following counts
            redis = await get_redis()
            await redis.incr(f"user_followers:{following_id}")
            await redis.incr(f"user_following:{follower_id}")
            
            db = await get_database()
            await db.event_logs.insert_one({
                "event": "user.followed",
                "follower_id": follower_id,
                "following_id": following_id,
                "timestamp": datetime.utcnow()
            })
            
            # Send notification to followed user (in production)
            # await send_notification(following_id, f"User {follower_id} started following you")
            
        except Exception as e:
            logger.error(f"❌ Handle user.followed error: {str(e)}")
    
    # ============ Utility Methods ============
    
    async def publish_event(self, channel: str, event_data: Dict):
        """
        Publish an event to Redis Pub/Sub
        
        Args:
            channel: Event channel name (e.g., 'post.created')
            event_data: Event data as dictionary
        """
        try:
            redis = await get_redis()
            
            event_json = json.dumps({
                **event_data,
                "published_at": datetime.utcnow().isoformat()
            })
            
            await redis.publish(channel, event_json)
            logger.info(f"📤 Event published: {channel}")
            
        except Exception as e:
            logger.error(f"❌ Publish event error: {str(e)}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Register a handler for specific event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        logger.info(f"📌 Subscribed handler to {event_type}")


# Singleton instance
event_consumer = EventConsumer()
