from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import DailyReport


async def get_daily_report(db: AsyncSession, report_date: date) -> DailyReport | None:
    result = await db.execute(select(DailyReport).where(DailyReport.report_date == report_date))
    return result.scalar_one_or_none()


async def get_or_create_daily_report(db: AsyncSession, report_date: date) -> DailyReport:
    report = await get_daily_report(db, report_date)
    if report is not None:
        return report

    report = DailyReport(report_date=report_date)
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report


async def save_morning_plan(db: AsyncSession, report_date: date, plan: str, tasks_planned: int = 0) -> DailyReport:
    report = await get_or_create_daily_report(db, report_date)
    report.morning_plan = plan
    report.tasks_planned = tasks_planned
    await db.flush()
    await db.refresh(report)
    return report


async def save_evening_summary(
    db: AsyncSession,
    report_date: date,
    summary: str,
    insights: list[str] | None = None,
    tasks_completed: int = 0,
    tasks_failed: int = 0,
    metrics_snapshot: dict | None = None,
) -> DailyReport:
    report = await get_or_create_daily_report(db, report_date)
    report.evening_summary = summary
    report.insights = insights or []
    report.tasks_completed = tasks_completed
    report.tasks_failed = tasks_failed
    report.metrics_snapshot = metrics_snapshot or {}
    await db.flush()
    await db.refresh(report)
    return report
