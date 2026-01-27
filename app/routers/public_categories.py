from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.category import CategoryOut
from app.repositories import category_repo

router = APIRouter(prefix="/public/categories", tags=["public-categories"])


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    return category_repo.list_categories(db)
