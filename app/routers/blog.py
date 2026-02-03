import uuid
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.core.config import settings
from app.core.deps import get_db, require_role
from app.db.models.user import User
from app.schemas.auth import MessageOut
from app.schemas.blog import BlogCreate, BlogOut, BlogUpdate
from app.services import blog_service
from app.repositories import category_repo

router = APIRouter(prefix="/blogs", tags=["blogs"])


def _save_image(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid image file")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")
    if file.size is not None and file.size > 3 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be 3 MB or smaller")

    media_root = Path(settings.MEDIA_DIR) / "blogs"
    media_root.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = media_root / filename
    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return f"/media/blogs/{filename}"


def _normalize_image_url(image_url: str | None) -> str | None:
    if not image_url:
        return None
    candidate = image_url.strip()
    if not candidate:
        return None
    if candidate.startswith("/"):
        return candidate
    parsed = urlparse(candidate)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return candidate
    raise HTTPException(status_code=400, detail="Image URL must be a valid http(s) URL or a /media path")


@router.get("", response_model=list[BlogOut])
@router.get("/", response_model=list[BlogOut])
def list_blogs(
    skip: int = 0,
    limit: int = 12,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> list[BlogOut]:
    return blog_service.list_blogs(db, skip=skip, limit=limit)


@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(
    blog_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> BlogOut:
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog


@router.post("", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
def create_blog(
    title: str = Form(...),
    content_html: str = Form(...),
    category_id: UUID = Form(...),
    status_value: str = Form("DRAFT"),
    excerpt_html: str = Form(...),
    image_url: str | None = Form(None),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
) -> BlogOut:
    category = category_repo.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")

    final_image_url = _normalize_image_url(image_url)
    if image_file is not None:
        final_image_url = _save_image(image_file)
    if not final_image_url:
        raise HTTPException(status_code=400, detail="Feature image is required")

    payload = BlogCreate(
        title=title,
        excerpt_html=excerpt_html,
        content_html=content_html,
        category_id=category_id,
        status=status_value,
        image_url=final_image_url,
        posted_by="Dr. Prem Thurairajah",
    )
    return blog_service.create_blog(db, current_user.id, payload)


@router.put("/{blog_id}", response_model=BlogOut)
def update_blog(
    blog_id: UUID,
    title: str | None = Form(None),
    content_html: str | None = Form(None),
    category_id: UUID | None = Form(None),
    status_value: str | None = Form(None),
    excerpt_html: str | None = Form(None),
    image_url: str | None = Form(None),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> BlogOut:
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if category_id is not None:
        category = category_repo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")

    final_image_url = _normalize_image_url(image_url)
    if image_file is not None:
        final_image_url = _save_image(image_file)

    payload = BlogUpdate(
        title=title,
        excerpt_html=excerpt_html,
        content_html=content_html,
        category_id=category_id,
        status=status_value,
        image_url=final_image_url,
    )
    return blog_service.update_blog(db, blog, payload)


@router.delete("/{blog_id}", response_model=MessageOut)
def delete_blog(
    blog_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> MessageOut:
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    blog_service.delete_blog(db, blog)
    return MessageOut(message="Blog deleted.")
