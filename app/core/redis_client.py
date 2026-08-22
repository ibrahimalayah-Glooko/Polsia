from app.config import settings

_clients: dict[int, object] = {}


def get_redis():
    """Lazily create and cache an async Redis client per running event loop.

    Celery tasks each spin up their own event loop via asyncio.run(), and a redis-py
    async client is bound to the loop it was created on — caching a single global
    client would raise "attached to a different loop" errors across task runs.
    """
    import asyncio

    import redis.asyncio as aioredis

    loop = asyncio.get_event_loop()
    key = id(loop)
    if key not in _clients:
        _clients[key] = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _clients[key]
