from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors()
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    logger.exception("Unexpected error occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error"
        },
    )
