from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.common import Amount, YearMonth


class BudgetSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Amount


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: YearMonth
    category_id: int
    amount: Decimal
