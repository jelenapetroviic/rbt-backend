import calendar
import datetime as dt
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Budget, Category, Transaction, TransactionType
from app.schemas.summary import CategorySummary, MonthlySummary

ZERO = Decimal("0.00")


def get_monthly_summary(db: Session, month: dt.date) -> MonthlySummary:
    last_day = month.replace(day=calendar.monthrange(month.year, month.month)[1])

    sums = db.execute(
        select(Transaction.category_id, Transaction.type, func.sum(Transaction.amount))
        .where(Transaction.date.between(month, last_day))
        .group_by(Transaction.category_id, Transaction.type)
    ).all()
    total_income = sum((s for _, kind, s in sums if kind == TransactionType.INCOME), ZERO)
    spent = {category_id: s for category_id, kind, s in sums if kind == TransactionType.EXPENSE}
    total_expense = sum(spent.values(), ZERO)

    budgets = dict(
        db.execute(select(Budget.category_id, Budget.amount).where(Budget.month == month)).all()
    )

    category_ids = spent.keys() | budgets.keys()
    categories = db.scalars(select(Category).where(Category.id.in_(category_ids))).all()
    lines = []
    for category in categories:
        category_spent = spent.get(category.id, ZERO)
        budget = budgets.get(category.id)
        lines.append(
            CategorySummary(
                category_id=category.id,
                name=category.name,
                color=category.color,
                spent=category_spent,
                budget=budget,
                remaining=None if budget is None else budget - category_spent,
            )
        )
    lines.sort(key=lambda line: (-line.spent, line.name.lower()))

    return MonthlySummary(
        month=month,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        categories=lines,
    )
