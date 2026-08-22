import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import redis_client
from app.core.events import ACTIVITY_CHANNEL
from app.core.serialization import model_to_dict
from app.models.report import ActivityLog


async def log_activity(
    db: AsyncSession,
    agent_type: str,
    action: str,
    summary: str,
    level: str = "info",
    detail: dict | None = None,
) -> ActivityLog:
    entry = ActivityLog(agent_type=agent_type, action=action, summary=summary, level=level, detail=detail)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)

    redis = redis_client.get_redis()
    await redis.publish(ACTIVITY_CHANNEL, json.dumps(model_to_dict(entry), default=str))

    return entry


async def get_recent_activity(db: AsyncSession, limit: int = 50) -> list[ActivityLog]:
    result = await db.execute(
        select(ActivityLog).order_by(ActivityLog.id.desc()).limit(limit)
    )
    return list(result.scalars().all())
