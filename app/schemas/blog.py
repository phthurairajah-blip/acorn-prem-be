from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class BlogCreate(BaseModel):
    title: str
    content: str

class BlogUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class BlogOut(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
