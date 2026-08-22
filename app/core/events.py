"""Redis pub/sub bridge used by the WebSocket activity feed."""
from app.core.redis_client import get_redis

ACTIVITY_CHANNEL = "polsia:activity"


async def subscribe_activity():
    """Return a Redis pubsub object subscribed to the activity channel."""
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(ACTIVITY_CHANNEL)
    return pubsub
