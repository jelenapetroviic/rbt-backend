import datetime as dt
import re
from decimal import Decimal
from typing import Annotated, Any

from pydantic import AfterValidator, BeforeValidator, Field, PlainSerializer, WithJsonSchema
from pydantic_core import PydanticCustomError

MAX_ID = 2**31 - 1
MAX_AMOUNT = Decimal("1000000.00")

_YEAR_MONTH = re.compile(r"[0-9]{4}-[0-9]{2}")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def no_nul_characters(value: str) -> str:
    if "\x00" in value:
        raise PydanticCustomError("nul_character", "Text must not contain NUL characters")
    return value


def _not_null(value: Any) -> Any:
    if value is None:
        raise PydanticCustomError("not_null", "Field can be left out, but not set to null")
    return value


def _parse_month(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if _YEAR_MONTH.fullmatch(value):
        try:
            return dt.datetime.strptime(value, "%Y-%m").date()
        except ValueError:
            pass
    raise PydanticCustomError("month_format", "Month must be in the format YYYY-MM")


def _require_iso_date(value: Any) -> Any:
    if isinstance(value, dt.date) or (isinstance(value, str) and _ISO_DATE.fullmatch(value)):
        return value
    raise PydanticCustomError("date_format", "Date must be in the format YYYY-MM-DD")


Id = Annotated[int, Field(gt=0, le=MAX_ID)]

Amount = Annotated[Decimal, Field(gt=0, le=MAX_AMOUNT, decimal_places=2, examples=["12.50"])]

#YYYY-MM
YearMonth = Annotated[
    dt.date,
    BeforeValidator(_parse_month),
    PlainSerializer(lambda month: f"{month.year:04d}-{month.month:02d}", return_type=str),
    WithJsonSchema({"type": "string", "pattern": r"^\d{4}-\d{2}$", "examples": ["2026-10"]}),
]

#YYYY-MM-DD
IsoDate = Annotated[dt.date, BeforeValidator(_require_iso_date)]

NotNull = AfterValidator(_not_null)
