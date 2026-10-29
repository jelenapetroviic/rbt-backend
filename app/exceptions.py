from collections.abc import Sequence

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError


class AppError(Exception):

    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidInputError(AppError):
    pass


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class ErrorResponse(BaseModel):
    detail: str


async def app_error_handler(_: Request, error: AppError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.message})


async def validation_error_handler(_: Request, error: RequestValidationError) -> JSONResponse:
    messages = [error_message(e["loc"][1:], e["msg"]) for e in error.errors()]
    return JSONResponse(status_code=400, content={"detail": "; ".join(messages)})


async def integrity_error_handler(_: Request, __: IntegrityError) -> JSONResponse:
    detail = "The data was changed by another request at the same time. Try again."
    return JSONResponse(status_code=409, content={"detail": detail})


def error_message(location: Sequence[str | int], message: str) -> str:
    field = ".".join(map(str, location))
    return f"{field}: {message}" if field else message
