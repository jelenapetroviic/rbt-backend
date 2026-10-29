from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.common import MAX_ID, YearMonth


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

CategoryId = Annotated[int, Path(gt=0, le=MAX_ID, description="ID of the category")]
TransactionId = Annotated[int, Path(gt=0, le=MAX_ID, description="ID of the transaction")]
Month = Annotated[YearMonth, Path(description="Month in the format YYYY-MM")]
