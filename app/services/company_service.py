from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyConfig
from app.models.report import DailyReport
from app.models.task import Task


async def set_website_url(db: AsyncSession, website_url: str) -> CompanyConfig | None:
    result = await db.execute(select(CompanyConfig).limit(1))
    company = result.scalar_one_or_none()
    if company is None:
        return None

    company.website_url = website_url
    await db.flush()
    await db.refresh(company)
    return company


async def get_full_context(db: AsyncSession) -> dict:
    """Build the context dict passed into every agent prompt."""
    result = await db.execute(select(CompanyConfig).limit(1))
    company = result.scalar_one_or_none()
    if company is None:
        return {}

    context: dict = {
        "company": {
            "name": company.name,
            "mission": company.mission,
            "vision": company.vision,
            "description": company.description,
            "target_market": company.target_market,
            "value_prop": company.value_prop,
            "github_repo": company.github_repo,
            "website_url": company.website_url,
        },
        "kpis": company.kpis or {},
        "goals": company.goals or {},
    }

    latest_report = await db.execute(
        select(DailyReport).order_by(DailyReport.report_date.desc()).limit(1)
    )
    report = latest_report.scalar_one_or_none()
    context["yesterday_summary"] = report.evening_summary if report else None

    todays_tasks = await db.execute(
        select(Task).where(Task.status.in_(["pending", "in_progress"])).limit(20)
    )
    context["todays_tasks"] = [
        {"title": t.title, "agent_type": t.agent_type, "status": t.status}
        for t in todays_tasks.scalars().all()
    ]

    return context


def build_context_prompt(context: dict) -> str:
    """Render the context dict as a plain-text prompt block for Claude."""
    if not context:
        return "No company context is configured yet."

    lines: list[str] = []
    company = context.get("company") or {}
    if company:
        lines.append(f"Company: {company.get('name')}")
        if company.get("mission"):
            lines.append(f"Mission: {company['mission']}")
        if company.get("description"):
            lines.append(f"Description: {company['description']}")

    kpis = context.get("kpis") or {}
    if kpis:
        lines.append(f"KPIs: {kpis}")

    if context.get("yesterday_summary"):
        lines.append(f"Yesterday's summary: {context['yesterday_summary']}")

    todays_tasks = context.get("todays_tasks") or []
    if todays_tasks:
        lines.append("Today's tasks:")
        for t in todays_tasks:
            lines.append(f"- [{t.get('agent_type')}] {t.get('title')} ({t.get('status')})")

    return "\n".join(lines)
