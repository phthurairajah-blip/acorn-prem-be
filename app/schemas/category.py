from uuid import UUID
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str | None = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    posts_count: int

    class Config:
        from_attributes = True
