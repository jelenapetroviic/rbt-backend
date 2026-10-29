from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.database import engine
from app.exceptions import (
    AppError,
    ErrorResponse,
    app_error_handler,
    integrity_error_handler,
    validation_error_handler,
)
from app.models import Base
from app.routers import budgets, categories, summary, transactions


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(
    title="Budget Tracker API",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        "4XX": {
            "model": ErrorResponse,
            "description": "400 invalid input, 404 not found, 409 a rule is broken",
        }
    },
)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)

app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(summary.router)
