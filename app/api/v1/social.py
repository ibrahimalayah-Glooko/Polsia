from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.social import SocialPost

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/posts")
async def get_posts(status: str | None = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    stmt = select(SocialPost).order_by(SocialPost.id.desc()).limit(limit)
    if status:
        stmt = stmt.where(SocialPost.status == status)
    result = await db.execute(stmt)
    return [model_to_dict(p) for p in result.scalars().all()]
