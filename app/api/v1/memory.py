from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.schemas.memory import MemoryCreate
from app.services.memory_service import list_memories, search_memory, store_memory

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("")
async def get_memory(
    q: str | None = None,
    category: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    if q:
        return await search_memory(db, q)
    entries = await list_memories(db, category=category, limit=limit)
    return [model_to_dict(e) for e in entries]


@router.post("", status_code=201)
async def post_memory(payload: MemoryCreate, db: AsyncSession = Depends(get_db)):
    entry = await store_memory(
        db,
        category=payload.category,
        title=payload.title,
        content=payload.content,
        source=payload.source,
        tags=payload.tags,
    )
    return model_to_dict(entry)
