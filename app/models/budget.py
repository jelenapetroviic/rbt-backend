import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Budget(Base):
    __tablename__ = "budgets"

    month: Mapped[dt.date] = mapped_column(Date, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(9, 2))
