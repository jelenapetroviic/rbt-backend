from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile, status

from app.dependencies import SessionDep, TransactionId
from app.models import Transaction
from app.schemas.csv_import import ImportResult
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilters,
    TransactionPage,
    TransactionRead,
    TransactionUpdate,
)
from app.services import csv_import
from app.services import transactions as service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionPage, summary="List transactions")
def list_transactions(
    filters: Annotated[TransactionFilters, Query()], db: SessionDep
) -> TransactionPage:
    """Newest first; transactions on the same date are listed last added first.
    The date range includes both dates.
    """
    return service.list_transactions(db, filters)


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a transaction",
)
def create_transaction(data: TransactionCreate, db: SessionDep) -> Transaction:
    return service.create_transaction(db, data)


@router.post("/import", response_model=ImportResult, summary="Import transactions from a CSV file")
def import_transactions(
    file: Annotated[
        UploadFile,
        File(
            description="CSV file in UTF-8, at most 1,000,000 rows. "
            "Header: type,amount,date,description,category"
        ),
    ],
    db: SessionDep,
) -> ImportResult:
    return csv_import.import_transactions(db, file.file)


@router.get("/{transaction_id}", response_model=TransactionRead, summary="Get a transaction")
def get_transaction(transaction_id: TransactionId, db: SessionDep) -> Transaction:
    return service.get_transaction(db, transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionRead, summary="Change a transaction")
def update_transaction(
    transaction_id: TransactionId, data: TransactionUpdate, db: SessionDep
) -> Transaction:
    return service.update_transaction(db, transaction_id, data)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
)
def delete_transaction(transaction_id: TransactionId, db: SessionDep) -> None:
    service.delete_transaction(db, transaction_id)
