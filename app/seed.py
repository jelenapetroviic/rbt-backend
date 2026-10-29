#python -m app.seed     150 random expenses
#python -m app.seed --expenses 5000

import argparse
import datetime as dt
import random
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Budget, Category, Transaction, TransactionType

MONTHS = 3
SALARY = Decimal("2500.00")
RENT = Decimal("700.00")

EXPENSE_CATEGORIES = {
    "Groceries": ("#4CAF50", "400.00", ["Supermarket", "Bakery", "Market"]),
    "Eating out": ("#FF9800", "300.00", ["Lunch", "Pizza", "Coffee"]),
    "Transport": ("#2196F3", "250.00", ["Bus ticket", "Taxi", "Fuel"]),
    "Entertainment": ("#E91E63", "350.00", ["Cinema", "Concert", "Books"]),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill the database with test data.")
    parser.add_argument(
        "--expenses", type=int, default=150, help="number of random expenses (default: 150)"
    )
    expenses = parser.parse_args().expenses

    Base.metadata.create_all(engine)
    today = dt.date.today()
    months = [_first_day_of_month(today, months_ago) for months_ago in range(MONTHS)]

    with SessionLocal() as db:
        salary = _get_or_create_category(db, "Salary", "#009688")
        rent = _get_or_create_category(db, "Rent", "#9C27B0")
        categories = {
            name: _get_or_create_category(db, name, color)
            for name, (color, _, _) in EXPENSE_CATEGORIES.items()
        }

        for month in months:
            db.add(_transaction(TransactionType.INCOME, SALARY, month, "Salary", salary))
            db.add(_transaction(TransactionType.EXPENSE, RENT, month, "Rent", rent))
            db.merge(Budget(month=month, category_id=rent.id, amount=RENT))
            for name, (_, budget, _) in EXPENSE_CATEGORIES.items():
                category_id = categories[name].id
                db.merge(Budget(month=month, category_id=category_id, amount=Decimal(budget)))

        first_day = months[-1]
        for _ in range(expenses):
            name = random.choice(list(EXPENSE_CATEGORIES))
            amount = Decimal(random.randint(100, 5000)) / 100
            date = first_day + dt.timedelta(days=random.randint(0, (today - first_day).days))
            description = random.choice(EXPENSE_CATEGORIES[name][2])
            db.add(
                _transaction(TransactionType.EXPENSE, amount, date, description, categories[name])
            )

        db.commit()

    print(
        f"Added {expenses + 2 * MONTHS} transactions and the budgets of "
        f"{first_day:%Y-%m} to {months[0]:%Y-%m} in {len(categories) + 2} categories."
    )


def _first_day_of_month(today: dt.date, months_ago: int) -> dt.date:
    year, month = divmod(today.year * 12 + today.month - 1 - months_ago, 12)
    return dt.date(year, month + 1, 1)


def _get_or_create_category(db: Session, name: str, color: str) -> Category:
    category = db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))
    if category is None:
        category = Category(name=name, color=color)
        db.add(category)
        db.flush()
    return category


def _transaction(
    type: TransactionType, amount: Decimal, date: dt.date, description: str, category: Category
) -> Transaction:
    return Transaction(
        type=type, amount=amount, date=date, description=description, category_id=category.id
    )


if __name__ == "__main__":
    main()
