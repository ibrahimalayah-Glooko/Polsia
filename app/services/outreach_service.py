from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outreach import Prospect


async def upsert_prospect(
    db: AsyncSession,
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    company: str | None = None,
    title: str | None = None,
    source: str = "email_outreach",
) -> Prospect:
    result = await db.execute(select(Prospect).where(Prospect.email == email))
    prospect = result.scalar_one_or_none()

    if prospect is not None:
        return prospect

    prospect = Prospect(
        email=email,
        first_name=first_name,
        last_name=last_name,
        company=company,
        title=title,
        source=source,
    )
    db.add(prospect)
    await db.flush()
    await db.refresh(prospect)
    return prospect
