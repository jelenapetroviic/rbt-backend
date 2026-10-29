from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import CategoryId, Month, SessionDep
from app.models import Budget
from app.schemas.budget import BudgetRead, BudgetSet
from app.schemas.common import YearMonth
from app.services import budgets as service

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=list[BudgetRead], summary="List the budgets of a month")
def list_budgets(
    month: Annotated[YearMonth, Query(description="Month in the format YYYY-MM")],
    db: SessionDep,
) -> Sequence[Budget]:
    """Sorted by category name."""
    return service.list_budgets(db, month)


@router.put(
    "/{month}/{category_id}",
    response_model=BudgetRead,
    summary="Set or change the budget of a category for a month",
)
def set_budget(month: Month, category_id: CategoryId, data: BudgetSet, db: SessionDep) -> Budget:
    return service.set_budget(db, month, category_id, data.amount)


@router.delete(
    "/{month}/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove the budget of a category for a month",
)
def delete_budget(month: Month, category_id: CategoryId, db: SessionDep) -> None:
    service.delete_budget(db, month, category_id)
