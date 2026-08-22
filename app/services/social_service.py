from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social import SocialPost


async def create_post(
    db: AsyncSession,
    platform: str,
    content: str,
    status: str = "draft",
    tweet_id: str | None = None,
) -> SocialPost:
    post = SocialPost(platform=platform, content=content, status=status, tweet_id=tweet_id)
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post
