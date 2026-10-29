from typing import Any

from pydantic import BaseModel, Field, ValidationInfo, field_validator
from pydantic_core import PydanticCustomError

from app.schemas.common import Id
from app.schemas.transaction import TransactionCreate

CSV_COLUMNS = ("type", "amount", "date", "description", "category")


class CsvRow(TransactionCreate):

    category_id: Id = Field(validation_alias="category")

    @field_validator("category_id", mode="before")
    @classmethod
    def find_category(cls, name: Any, info: ValidationInfo) -> Any:
        name = str(name).strip()
        category_id = info.context["category_ids"].get(name.lower())
        if category_id is None:
            raise PydanticCustomError(
                "unknown_category", "Category '{name}' does not exist", {"name": name}
            )
        return category_id


class RowError(BaseModel):
    row: int = Field(description="Line of the row in the file; the header is line 1")
    errors: list[str] = Field(examples=[["amount: Input should be greater than 0"]])


class ImportResult(BaseModel):
    imported: int = Field(description="Number of transactions that were imported")
    failed: int = Field(description="Number of rows that were not imported")
    errors: list[RowError] = Field(description="The rows that were not imported and why")
