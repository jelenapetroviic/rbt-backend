import datetime as dt
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

DESCRIPTION_MAX_LENGTH = 200


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType,
            name="transaction_type",
            
            values_callable=lambda enum: [member.value for member in enum],
        )
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(9, 2))
    date: Mapped[dt.date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(String(DESCRIPTION_MAX_LENGTH))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
