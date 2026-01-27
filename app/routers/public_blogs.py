import time
from collections import defaultdict, deque
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.repositories import blog_repo
from app.schemas.blog import BlogOut

router = APIRouter(prefix="/public/blogs", tags=["public-blogs"])

_RATE_LIMIT = 100
_WINDOW_SECONDS = 60
_request_log: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _WINDOW_SECONDS
    bucket = _request_log[ip]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    bucket.append(now)


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
