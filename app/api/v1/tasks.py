from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.schemas.task import TaskCreate
from app.services.task_service import create_task, get_task, list_tasks

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("")
async def get_tasks(
    status: str | None = None,
    agent_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    tasks = await list_tasks(db, status=status, agent_type=agent_type)
    return [model_to_dict(t) for t in tasks]


@router.post("", status_code=201)
async def post_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = await create_task(
        db,
        title=payload.title,
        agent_type=payload.agent_type,
        description=payload.description,
        priority=payload.priority,
        scheduled_date=payload.scheduled_date,
    )
    return model_to_dict(task)


@router.get("/{task_id}")
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return model_to_dict(task)
