from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, StringConstraints

from app.models.category import CATEGORY_NAME_MAX_LENGTH
from app.schemas.common import NotNull, no_nul_characters

CategoryName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=CATEGORY_NAME_MAX_LENGTH),
    AfterValidator(no_nul_characters),
]

HexColor = Annotated[str, StringConstraints(pattern=r"^#[0-9A-Fa-f]{6}$")]


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: CategoryName
    color: HexColor


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[CategoryName | None, NotNull] = None
    color: Annotated[HexColor | None, NotNull] = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str
