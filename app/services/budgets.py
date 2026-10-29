import datetime as dt
from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models import Budget, Category
from app.services.categories import get_category


def list_budgets(db: Session, month: dt.date) -> Sequence[Budget]:
    query = (
        select(Budget)
        .join(Category, Category.id == Budget.category_id)
        .where(Budget.month == month)
        .order_by(func.lower(Category.name), Category.id)
    )
    return db.scalars(query).all()


def set_budget(db: Session, month: dt.date, category_id: int, amount: Decimal) -> Budget:
    get_category(db, category_id)  # 404 if the category does not exist
    budget = db.get(Budget, (month, category_id))
    if budget is None:
        budget = Budget(month=month, category_id=category_id, amount=amount)
        db.add(budget)
    else:
        budget.amount = amount
    db.commit()
    return budget


def delete_budget(db: Session, month: dt.date, category_id: int) -> None:
    budget = db.get(Budget, (month, category_id))
    if budget is None:
        raise NotFoundError(f"Category {category_id} has no budget for {month:%Y-%m}")
    db.delete(budget)
    db.commit()
