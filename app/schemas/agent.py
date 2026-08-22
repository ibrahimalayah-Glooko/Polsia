from pydantic import BaseModel


class AgentTriggerRequest(BaseModel):
    task_title: str | None = None
    task_description: str | None = None
