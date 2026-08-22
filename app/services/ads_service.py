from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ads import AdCampaign


async def create_campaign(
    db: AsyncSession,
    platform: str,
    name: str,
    goal: str | None = None,
    daily_budget_usd: float = 0,
) -> AdCampaign:
    campaign = AdCampaign(platform=platform, name=name, goal=goal, daily_budget_usd=daily_budget_usd)
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign
