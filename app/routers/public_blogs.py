from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.rate_limit import RateLimiter, get_client_ip
from app.repositories import blog_repo
from app.schemas.blog import BlogOut

router = APIRouter(prefix="/public/blogs", tags=["public-blogs"])

_public_blog_limiter = RateLimiter(
    max_attempts=settings.PUBLIC_BLOG_MAX_ATTEMPTS,
    window_seconds=settings.PUBLIC_BLOG_WINDOW_SECONDS,
    error_detail="Rate limit exceeded",
)


def rate_limit(request: Request) -> None:
    ip = get_client_ip(request)
    _public_blog_limiter.hit(ip)


@router.get("/", response_model=list[BlogOut])
def list_published_blogs(
    request: Request,
    skip: int = 0,
    limit: int = 12,
    db: Session = Depends(get_db),
) -> list[BlogOut]:
    rate_limit(request)
    return blog_repo.list_published_blogs(db, skip=skip, limit=limit)


@router.get("/{blog_id}", response_model=BlogOut)
def get_published_blog(
    blog_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
) -> BlogOut:
    rate_limit(request)
    blog = blog_repo.get_published_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog
