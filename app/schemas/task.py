from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    agent_type: str
    description: str | None = None
    priority: int = 3
    scheduled_date: datetime | None = None
