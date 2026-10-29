from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import YearMonth


class CategorySummary(BaseModel):
    category_id: int
    name: str
    color: str
    spent: Decimal = Field(description="Sum of the category's expenses in the month")
    budget: Decimal | None = Field(description="Budget for the month, or null if none is set")
    remaining: Decimal | None = Field(
        description="Budget minus spent; negative when over budget, null without a budget"
    )


class MonthlySummary(BaseModel):
    month: YearMonth
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal = Field(description="Income minus expense; can be negative")
    categories: list[CategorySummary] = Field(
        description="Categories with an expense or a budget in the month, "
        "highest expense first, then by name"
    )
