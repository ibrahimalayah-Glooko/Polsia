import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.finance import ExpenseRecord, RevenueSnapshot, StripeEvent

router = APIRouter()


@router.get("/summary", dependencies=[Depends(verify_api_key)])
async def get_finance_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RevenueSnapshot).order_by(RevenueSnapshot.snapshot_date.desc()).limit(1))
    snapshot = result.scalar_one_or_none()

    expenses_result = await db.execute(select(ExpenseRecord))
    total_expenses_cents = sum(e.amount_cents for e in expenses_result.scalars().all())

    return {
        "mrr_cents": snapshot.mrr_cents if snapshot else 0,
        "arr_cents": snapshot.arr_cents if snapshot else 0,
        "active_subscribers": snapshot.active_subscribers if snapshot else 0,
        "total_ad_spend_usd": 0,
        "total_expenses_month_cents": total_expenses_cents,
        "stripe_balance_cents": snapshot.stripe_balance_cents if snapshot else 0,
        "last_snapshot_date": snapshot.snapshot_date.isoformat() if snapshot else None,
    }


@router.get("/revenue", dependencies=[Depends(verify_api_key)])
async def get_revenue_history(limit: int = 30, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RevenueSnapshot).order_by(RevenueSnapshot.snapshot_date.desc()).limit(limit)
    )
    return [model_to_dict(s) for s in result.scalars().all()]


@router.get("/expenses", dependencies=[Depends(verify_api_key)])
async def get_expenses(category: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ExpenseRecord).order_by(ExpenseRecord.date.desc())
    if category:
        stmt = stmt.where(ExpenseRecord.category == category)
    result = await db.execute(stmt)
    return [model_to_dict(e) for e in result.scalars().all()]


@router.get("/events", dependencies=[Depends(verify_api_key)])
async def get_stripe_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StripeEvent).order_by(StripeEvent.id.desc()))
    return [model_to_dict(e) for e in result.scalars().all()]


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook secret is not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    import stripe

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Stripe signature: {exc}") from exc

    data = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event["data"]["object"]

    stripe_event = StripeEvent(
        stripe_event_id=event["id"],
        event_type=event["type"],
        customer_id=data.get("customer"),
        amount_cents=data.get("amount"),
        currency=data.get("currency"),
        raw_payload=json.loads(payload),
    )
    db.add(stripe_event)
    await db.flush()

    return {"status": "received"}
