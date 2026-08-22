from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import AgentRun, Task

VALID_AGENT_TYPES = [
    "orchestrator",
    "business_planning",
    "competitor_research",
    "social_media",
    "email_outreach",
    "customer_support",
    "ads_management",
    "code_generation",
    "finance",
]


async def create_task(
    db: AsyncSession,
    title: str,
    agent_type: str,
    description: str | None = None,
    priority: int = 3,
    source: str = "manual",
    scheduled_date: datetime | None = None,
) -> Task:
    task = Task(
        title=title,
        agent_type=agent_type,
        description=description,
        priority=priority,
        source=source,
        scheduled_date=scheduled_date,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: int,
    status: str,
    result_summary: str | None = None,
    error_message: str | None = None,
) -> Task | None:
    task = await get_task(db, task_id)
    if task is None:
        return None

    task.status = status
    if result_summary is not None:
        task.result_summary = result_summary
    if error_message is not None:
        task.error_message = error_message

    await db.flush()
    await db.refresh(task)
    return task


async def list_tasks(db: AsyncSession, status: str | None = None, agent_type: str | None = None) -> list[Task]:
    stmt = select(Task).order_by(Task.id.desc())
    if status:
        stmt = stmt.where(Task.status == status)
    if agent_type:
        stmt = stmt.where(Task.agent_type == agent_type)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_tasks_today_summary(db: AsyncSession) -> dict:
    today_start = datetime.combine(date.today(), datetime.min.time())

    async def _count(*conditions):
        stmt = select(func.count(Task.id)).where(Task.created_at >= today_start, *conditions)
        result = await db.execute(stmt)
        return result.scalar() or 0

    return {
        "total": await _count(),
        "completed": await _count(Task.status == "completed"),
        "pending": await _count(Task.status.in_(["pending", "in_progress"])),
        "failed": await _count(Task.status == "failed"),
    }


async def create_agent_run(
    db: AsyncSession,
    agent_type: str,
    task_id: int | None = None,
    input_context: dict | None = None,
) -> AgentRun:
    run = AgentRun(agent_type=agent_type, task_id=task_id, input_context=input_context)
    db.add(run)
    await db.flush()
    await db.refresh(run)
    return run


async def finish_agent_run(
    db: AsyncSession,
    run_id: int,
    status: str,
    output: dict | None = None,
    duration_secs: float | None = None,
) -> AgentRun | None:
    result = await db.execute(select(AgentRun).where(AgentRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        return None

    run.status = status
    run.output = output
    run.duration_secs = duration_secs
    run.ended_at = datetime.utcnow()

    await db.flush()
    await db.refresh(run)
    return run


async def get_last_agent_run(db: AsyncSession, agent_type: str) -> AgentRun | None:
    result = await db.execute(
        select(AgentRun).where(AgentRun.agent_type == agent_type).order_by(AgentRun.id.desc()).limit(1)
    )
    return result.scalar_one_or_none()
