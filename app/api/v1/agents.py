from enum import Enum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.schemas.agent import AgentTriggerRequest
from app.services.task_service import (
    VALID_AGENT_TYPES,
    create_task,
    get_last_agent_run,
    list_tasks,
)

AgentTypeEnum = Enum(  # type: ignore[misc]
    "AgentTypeEnum", {name: name for name in VALID_AGENT_TYPES}, type=str
)

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/{agent_type}/trigger", status_code=202)
async def trigger_agent(
    agent_type: AgentTypeEnum,
    payload: AgentTriggerRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    payload = payload or AgentTriggerRequest()
    task = await create_task(
        db,
        title=payload.task_title or f"Manually triggered {agent_type.value} run",
        agent_type=agent_type.value,
        description=payload.task_description,
        source="manual",
    )
    await db.flush()

    from celery_app.tasks.agent_tasks import run_agent_task

    run_agent_task.delay(task.id)

    return {"status": "queued", "task_id": task.id}


@router.get("/status")
async def get_agent_status(db: AsyncSession = Depends(get_db)):
    statuses = []
    for agent_type in VALID_AGENT_TYPES:
        last_run = await get_last_agent_run(db, agent_type)
        tasks_for_agent = await list_tasks(db, agent_type=agent_type)
        statuses.append(
            {
                "agent_type": agent_type,
                "last_run_at": last_run.started_at.isoformat() if last_run else None,
                "last_run_status": last_run.status if last_run else None,
                "tasks_today": sum(1 for t in tasks_for_agent),
                "tasks_total": len(tasks_for_agent),
            }
        )
    return statuses
