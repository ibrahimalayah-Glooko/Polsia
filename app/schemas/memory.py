from pydantic import BaseModel


class MemoryCreate(BaseModel):
    category: str
    title: str
    content: str
    source: str | None = None
    tags: list[str] | None = None
