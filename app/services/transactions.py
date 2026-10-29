from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.exceptions import InvalidInputError, NotFoundError
from app.models import Category, Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilters,
    TransactionPage,
    TransactionRead,
    TransactionUpdate,
)


def list_transactions(db: Session, filters: TransactionFilters) -> TransactionPage:
    conditions = _filter_conditions(filters)
    total = db.scalar(select(func.count()).select_from(Transaction).where(*conditions))
    transactions = db.scalars(
        select(Transaction)
        .where(*conditions)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    ).all()
    return TransactionPage(
        items=[TransactionRead.model_validate(transaction) for transaction in transactions],
        total=total or 0,
        page=filters.page,
        page_size=filters.page_size,
    )


def get_transaction(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise NotFoundError(f"Transaction {transaction_id} not found")
    return transaction


def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    _ensure_category_exists(db, data.category_id)
    transaction = Transaction(**data.model_dump())
    db.add(transaction)
    db.commit()
    return transaction


def update_transaction(db: Session, transaction_id: int, data: TransactionUpdate) -> Transaction:
    transaction = get_transaction(db, transaction_id)
    changes = data.model_dump(exclude_unset=True)
    if "category_id" in changes:
        _ensure_category_exists(db, changes["category_id"])
    for field, value in changes.items():
        setattr(transaction, field, value)
    db.commit()
    return transaction


def delete_transaction(db: Session, transaction_id: int) -> None:
    db.delete(get_transaction(db, transaction_id))
    db.commit()


def _ensure_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise InvalidInputError(f"Category {category_id} does not exist")


def _filter_conditions(filters: TransactionFilters) -> list[ColumnElement[bool]]:
    conditions = []
    if filters.date_from is not None:
        conditions.append(Transaction.date >= filters.date_from)
    if filters.date_to is not None:
        conditions.append(Transaction.date <= filters.date_to)
    if filters.category_id is not None:
        conditions.append(Transaction.category_id == filters.category_id)
    if filters.type is not None:
        conditions.append(Transaction.type == filters.type)
    if filters.q is not None:
        text = filters.q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        conditions.append(Transaction.description.ilike(f"%{text}%", escape="\\"))
    return conditions
