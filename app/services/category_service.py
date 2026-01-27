from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import category_repo
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.db.models.category import Category


def list_categories(db: Session) -> list[Category]:
    return category_repo.list_categories(db)


def create_category(db: Session, data: CategoryCreate) -> Category:
    existing = category_repo.get_by_name(db, data.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    return category_repo.create(db, data)


def get_category(db: Session, category_id: UUID) -> Category | None:
    return category_repo.get_by_id(db, category_id)


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    if data.name is not None:
        existing = category_repo.get_by_name(db, data.name)
        if existing and existing.id != category.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    return category_repo.update(db, category, data)


def delete_category(db: Session, category: Category) -> None:
    category_repo.delete(db, category)
