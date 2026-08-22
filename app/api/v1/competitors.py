from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.competitor import Competitor

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("")
async def get_competitors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competitor).order_by(Competitor.id.desc()))
    return [model_to_dict(c) for c in result.scalars().all()]
