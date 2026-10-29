from collections.abc import Sequence

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models import Category, Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> Sequence[Category]:
    query = select(Category).order_by(func.lower(Category.name), Category.id)
    return db.scalars(query).all()


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise NotFoundError(f"Category {category_id} not found")
    return category


def create_category(db: Session, data: CategoryCreate) -> Category:
    _ensure_name_is_free(db, data.name)
    category = Category(name=data.name, color=data.color)
    db.add(category)
    db.commit()
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        _ensure_name_is_free(db, changes["name"], ignore_id=category_id)
    for field, value in changes.items():
        setattr(category, field, value)
    db.commit()
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    if db.scalar(select(exists().where(Transaction.category_id == category_id))):
        raise ConflictError(f"Category {category_id} has transactions and cannot be deleted")
    db.delete(category)
    db.commit()


def _ensure_name_is_free(db: Session, name: str, ignore_id: int | None = None) -> None:
    query = select(Category.id).where(func.lower(Category.name) == func.lower(name))
    if ignore_id is not None:
        query = query.where(Category.id != ignore_id)
    if db.scalar(query) is not None:
        raise ConflictError(f"A category named '{name}' already exists")
