from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogUpdate


def create(db: Session, author_id: UUID, data: BlogCreate) -> Blog:
    blog = Blog(
        title=data.title,
        content_html=data.content_html,
        category_id=data.category_id,
        status=data.status,
        image_url=data.image_url,
        posted_by=data.posted_by or "Dr. Prem Thurairajah",
        author_id=author_id,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def list_blogs(db: Session, skip: int = 0, limit: int = 12) -> list[Blog]:
    return (
        db.query(Blog)
        .order_by(Blog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_published_blogs(db: Session, skip: int = 0, limit: int = 12) -> list[Blog]:
    return (
        db.query(Blog)
        .filter(Blog.status == "PUBLISHED")
        .order_by(Blog.published_at.desc().nullslast(), Blog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get(db: Session, blog_id: UUID) -> Blog | None:
    return db.get(Blog, blog_id)


def get_published_blog(db: Session, blog_id: UUID) -> Blog | None:
    return db.query(Blog).filter(Blog.id == blog_id, Blog.status == "PUBLISHED").first()


def update(db: Session, blog: Blog, data: BlogUpdate) -> Blog:
    if data.title is not None:
        blog.title = data.title
    if data.content_html is not None:
        blog.content_html = data.content_html
    if data.category_id is not None:
        blog.category_id = data.category_id
    if data.status is not None:
        blog.status = data.status
    if data.image_url is not None:
        blog.image_url = data.image_url
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def delete(db: Session, blog: Blog) -> None:
    db.delete(blog)
    db.commit()
