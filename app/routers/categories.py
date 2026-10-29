from collections.abc import Sequence

from fastapi import APIRouter, status

from app.dependencies import CategoryId, SessionDep
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import categories as service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead], summary="List categories")
def list_categories(db: SessionDep) -> Sequence[Category]:
    """All categories, sorted by name."""
    return service.list_categories(db)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(data: CategoryCreate, db: SessionDep) -> Category:
    return service.create_category(db, data)


@router.get("/{category_id}", response_model=CategoryRead, summary="Get a category")
def get_category(category_id: CategoryId, db: SessionDep) -> Category:
    return service.get_category(db, category_id)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Change the name or color of a category",
)
def update_category(category_id: CategoryId, data: CategoryUpdate, db: SessionDep) -> Category:
    return service.update_category(db, category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category and its budgets",
)
def delete_category(category_id: CategoryId, db: SessionDep) -> None:
    """A category that has transactions cannot be deleted (409)."""
    service.delete_category(db, category_id)
