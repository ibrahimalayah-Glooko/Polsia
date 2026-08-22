from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.outreach import Prospect

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/prospects")
async def get_prospects(status: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)):
    stmt = select(Prospect).order_by(Prospect.id.desc()).limit(limit)
    if status:
        stmt = stmt.where(Prospect.status == status)
    result = await db.execute(stmt)
    return [model_to_dict(p) for p in result.scalars().all()]
