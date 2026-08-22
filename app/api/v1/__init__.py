from fastapi import APIRouter

from app.api.v1 import (
    ads,
    agents,
    competitors,
    config,
    dashboard,
    finance,
    health,
    memory,
    outreach,
    social,
    tasks,
)

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(config.router, prefix="/config", tags=["config"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(finance.router, prefix="/finance", tags=["finance"])
router.include_router(memory.router, prefix="/memory", tags=["memory"])
router.include_router(social.router, prefix="/social", tags=["social"])
router.include_router(ads.router, prefix="/ads", tags=["ads"])
router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
