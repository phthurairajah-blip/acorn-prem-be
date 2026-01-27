from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import blog_repo
from app.schemas.blog import BlogCreate, BlogUpdate
from app.db.models.blog import Blog

ALLOWED_STATUSES = {"DRAFT", "PUBLISHED"}


def _normalize_status(value: str | None) -> str | None:
    if value is None:
        return None
    status_value = value.upper()
    if status_value not in ALLOWED_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    return status_value


def create_blog(db: Session, author_id, data: BlogCreate) -> Blog:
    status_value = _normalize_status(data.status) or "DRAFT"
    data.status = status_value
    blog = blog_repo.create(db, author_id, data)
    if blog.status == "PUBLISHED" and blog.published_at is None:
        blog.published_at = datetime.now(timezone.utc)
        db.add(blog)
        db.commit()
        db.refresh(blog)
    return blog


def list_blogs(db: Session, skip: int = 0, limit: int = 12) -> list[Blog]:
    return blog_repo.list_blogs(db, skip=skip, limit=limit)


def get_blog(db: Session, blog_id) -> Blog | None:
    return blog_repo.get(db, blog_id)


def update_blog(db: Session, blog: Blog, data: BlogUpdate) -> Blog:
    status_value = _normalize_status(data.status)
    data.status = status_value if status_value is not None else data.status
    updated = blog_repo.update(db, blog, data)
    if updated.status == "PUBLISHED" and updated.published_at is None:
        updated.published_at = datetime.now(timezone.utc)
        db.add(updated)
        db.commit()
        db.refresh(updated)
    return updated


def delete_blog(db: Session, blog: Blog) -> None:
    blog_repo.delete(db, blog)
