from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.serialization import model_to_dict
from app.models.company import CompanyConfig
from app.models.report import DailyReport
from app.services.activity_service import get_recent_activity
from app.services.task_service import VALID_AGENT_TYPES, get_tasks_today_summary

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CompanyConfig).limit(1))
    company = result.scalar_one_or_none()
    kpis = company.kpis if company and company.kpis else {}

    tasks_summary = await get_tasks_today_summary(db)

    latest_report = await db.execute(select(DailyReport).order_by(DailyReport.report_date.desc()).limit(1))
    report = latest_report.scalar_one_or_none()

    return {
        "tasks_today_total": tasks_summary["total"],
        "tasks_today_completed": tasks_summary["completed"],
        "tasks_today_pending": tasks_summary["pending"],
        "tasks_today_failed": tasks_summary["failed"],
        "active_agents": VALID_AGENT_TYPES,
        "kpis": kpis,
        "last_report_date": report.report_date.isoformat() if report else None,
    }


@router.get("/activity")
async def get_activity(limit: int = 50, db: AsyncSession = Depends(get_db)):
    entries = await get_recent_activity(db, limit=limit)
    return [model_to_dict(e) for e in entries]


@router.get("/reports/daily")
async def get_latest_daily_report(report_date: date | None = None, db: AsyncSession = Depends(get_db)):
    target_date = report_date or date.today()
    result = await db.execute(select(DailyReport).where(DailyReport.report_date == target_date))
    report = result.scalar_one_or_none()
    return model_to_dict(report) if report else None
