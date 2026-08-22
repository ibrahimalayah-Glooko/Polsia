from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.ads import AdCampaign

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/campaigns")
async def get_campaigns(platform: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(AdCampaign).order_by(AdCampaign.id.desc())
    if platform:
        stmt = stmt.where(AdCampaign.platform == platform)
    result = await db.execute(stmt)
    return [model_to_dict(c) for c in result.scalars().all()]
