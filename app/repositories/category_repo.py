from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.category import Category
from app.db.models.blog import Blog
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_by_id(db: Session, category_id: UUID) -> Category | None:
    return db.get(Category, category_id)


def get_by_name(db: Session, name: str) -> Category | None:
    return db.query(Category).filter(func.lower(Category.name) == name.lower()).first()


def list_categories(db: Session) -> list[Category]:
    categories = db.query(Category).order_by(Category.name.asc()).all()
    counts = (
        db.query(Blog.category_id, func.count(Blog.id))
        .group_by(Blog.category_id)
        .all()
    )
    count_map = {category_id: total for category_id, total in counts}
    for category in categories:
        category.posts_count = int(count_map.get(category.id, 0))
    return categories


def create(db: Session, data: CategoryCreate) -> Category:
    category = Category(name=data.name.strip())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update(db: Session, category: Category, data: CategoryUpdate) -> Category:
    if data.name is not None:
        category.name = data.name.strip()
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
