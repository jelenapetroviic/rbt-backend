import datetime as dt
from decimal import Decimal
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from app.models.transaction import DESCRIPTION_MAX_LENGTH, TransactionType
from app.schemas.common import Amount, Id, IsoDate, NotNull, no_nul_characters

MAX_PAGE = 1_000_000
MAX_PAGE_SIZE = 100

Description = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=DESCRIPTION_MAX_LENGTH),
    AfterValidator(no_nul_characters),
    AfterValidator(lambda text: text or None),
]

SearchText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=DESCRIPTION_MAX_LENGTH),
    AfterValidator(no_nul_characters),
]


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: TransactionType
    amount: Amount
    date: IsoDate
    description: Description | None = None
    category_id: Id


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Annotated[TransactionType | None, NotNull] = None
    amount: Annotated[Amount | None, NotNull] = None
    date: Annotated[IsoDate | None, NotNull] = None
    description: Description | None = None
    category_id: Annotated[Id | None, NotNull] = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TransactionType
    amount: Decimal
    date: dt.date
    description: str | None
    category_id: int


class TransactionPage(BaseModel):
    items: list[TransactionRead]
    total: int = Field(description="Number of transactions matching the filters, on all pages")
    page: int
    page_size: int


class TransactionFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_from: IsoDate | None = Field(None, description="Only transactions on or after this date")
    date_to: IsoDate | None = Field(None, description="Only transactions on or before this date")
    category_id: Id | None = Field(None, description="Only transactions in this category")
    type: TransactionType | None = Field(None, description="Only income or only expenses")
    q: SearchText | None = Field(None, description="Text in the description, ignoring case")
    page: int = Field(1, ge=1, le=MAX_PAGE)
    page_size: int = Field(20, ge=1, le=MAX_PAGE_SIZE)

    @model_validator(mode="after")
    def check_date_range(self) -> Self:
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        return self
