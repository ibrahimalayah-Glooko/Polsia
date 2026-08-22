from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance import RevenueSnapshot


async def upsert_todays_snapshot(
    db: AsyncSession,
    mrr_cents: int = 0,
    arr_cents: int = 0,
    active_subscribers: int = 0,
    stripe_balance_cents: int = 0,
) -> RevenueSnapshot:
    today = date.today()
    result = await db.execute(select(RevenueSnapshot).where(RevenueSnapshot.snapshot_date == today))
    snapshot = result.scalar_one_or_none()

    if snapshot is None:
        snapshot = RevenueSnapshot(snapshot_date=today)
        db.add(snapshot)

    snapshot.mrr_cents = mrr_cents
    snapshot.arr_cents = arr_cents
    snapshot.active_subscribers = active_subscribers
    snapshot.stripe_balance_cents = stripe_balance_cents

    await db.flush()
    await db.refresh(snapshot)
    return snapshot
