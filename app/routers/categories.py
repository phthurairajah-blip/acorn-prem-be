from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.db.models.user import User
from app.schemas.auth import MessageOut
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> list[CategoryOut]:
    return category_service.list_categories(db)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> CategoryOut:
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> CategoryOut:
    return category_service.create_category(db, payload)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> CategoryOut:
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category_service.update_category(db, category, payload)


@router.delete("/{category_id}", response_model=MessageOut)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> MessageOut:
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category_service.delete_category(db, category)
    return MessageOut(message="Category deleted.")
