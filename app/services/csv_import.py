import csv
import io
from collections.abc import Iterator
from typing import Any, BinaryIO

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import InvalidInputError, error_message
from app.models import Category
from app.schemas.csv_import import CSV_COLUMNS, CsvRow, ImportResult, RowError

MAX_ROWS = 1_000_000

_COPY_TRANSACTIONS = "COPY transactions (type, amount, date, description, category_id) FROM STDIN"


def import_transactions(db: Session, file: BinaryIO) -> ImportResult:
    records = _read_csv(file)
    _, header = next(records, (1, []))
    columns = [name.strip().lower() for name in header]
    if sorted(columns) != sorted(CSV_COLUMNS):
        raise InvalidInputError(f"The first line must name the columns {','.join(CSV_COLUMNS)}")

    category_ids = {
        name.lower(): id_ for id_, name in db.execute(select(Category.id, Category.name))
    }
    context = {"category_ids": category_ids}
    imported = 0
    errors: list[RowError] = []

    connection = db.connection().connection.driver_connection
    with connection.cursor() as cursor, cursor.copy(_COPY_TRANSACTIONS) as copy:
        for count, (line, values) in enumerate(records, start=1):
            if count > MAX_ROWS:
                raise InvalidInputError(f"The file has more than {MAX_ROWS:,} rows")
            row = _parse_row(columns, values, context)
            if isinstance(row, CsvRow):
                copy.write_row(
                    (row.type.value, row.amount, row.date, row.description, row.category_id)
                )
                imported += 1
            else:
                errors.append(RowError(row=line, errors=row))

    db.commit()
    return ImportResult(imported=imported, failed=len(errors), errors=errors)


def _read_csv(file: BinaryIO) -> Iterator[tuple[int, list[str]]]:
    reader = csv.reader(io.TextIOWrapper(file, encoding="utf-8-sig", newline=""))
    line = 1
    try:
        for values in reader:
            if values:
                yield line, values
            line = reader.line_num + 1
    except UnicodeDecodeError:
        raise InvalidInputError("The file must be a CSV file in UTF-8") from None
    except csv.Error as error:
        raise InvalidInputError(f"Line {reader.line_num}: {error}") from None


def _parse_row(
    columns: list[str], values: list[str], context: dict[str, Any]
) -> CsvRow | list[str]:
    if len(values) != len(columns):
        return [f"Expected {len(columns)} values, found {len(values)}"]
    try:
        return CsvRow.model_validate(dict(zip(columns, values, strict=True)), context=context)
    except ValidationError as error:
        return [error_message(e["loc"], e["msg"]) for e in error.errors()]
