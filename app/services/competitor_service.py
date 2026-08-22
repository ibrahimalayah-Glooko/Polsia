from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import Competitor


async def upsert_competitor(
    db: AsyncSession,
    name: str,
    website: str | None = None,
    positioning: str | None = None,
    strengths: list[str] | None = None,
    weaknesses: list[str] | None = None,
) -> Competitor:
    result = await db.execute(select(Competitor).where(Competitor.name == name))
    competitor = result.scalar_one_or_none()

    if competitor is None:
        competitor = Competitor(name=name)
        db.add(competitor)

    competitor.website = website
    competitor.positioning = positioning
    competitor.strengths = strengths
    competitor.weaknesses = weaknesses

    await db.flush()
    await db.refresh(competitor)
    return competitor
