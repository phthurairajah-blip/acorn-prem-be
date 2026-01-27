from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    excerpt_html: str
    content_html: str
    category_id: UUID
    status: str = "DRAFT"
    image_url: str
    posted_by: str | None = None


class BlogUpdate(BaseModel):
    title: str | None = None
    excerpt_html: str | None = None
    content_html: str | None = None
    category_id: UUID | None = None
    status: str | None = None
    image_url: str | None = None


class BlogOut(BaseModel):
    id: UUID
    title: str
    excerpt_html: str
    content_html: str
    status: str
    image_url: str | None = None
    posted_by: str
    category_id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None

    class Config:
        from_attributes = True
