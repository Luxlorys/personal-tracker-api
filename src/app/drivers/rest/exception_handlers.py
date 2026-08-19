"""Where domain and application errors become HTTP status codes.

This mapping is the drivers layer's job. Inner layers raise meaningful errors and
stay unaware that HTTP exists.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.adapters.exceptions import ExternalError
from app.domain.exceptions import (
    CadenceAlreadyMetError,
    DomainError,
    HabitArchivedError,
)
from app.use_cases.exceptions import FutureCheckInError, HabitNotFoundError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HabitNotFoundError)
    async def habit_not_found_handler(request: Request, exc: HabitNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc)})

    @app.exception_handler(CadenceAlreadyMetError)
    async def cadence_already_met_handler(request: Request, exc: CadenceAlreadyMetError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": str(exc)})

    @app.exception_handler(HabitArchivedError)
    async def habit_archived_handler(request: Request, exc: HabitArchivedError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": str(exc)})

    @app.exception_handler(FutureCheckInError)
    async def future_check_in_handler(request: Request, exc: FutureCheckInError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"message": str(exc)})

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        """Catch-all for rules without a more specific mapping."""
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"message": str(exc)})

    @app.exception_handler(ExternalError)
    async def external_error_handler(request: Request, exc: ExternalError) -> JSONResponse:
        logger.error("External system failed on %s %s: %s", request.method, request.url.path, exc, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": "Something went wrong. Please try again"},
        )
