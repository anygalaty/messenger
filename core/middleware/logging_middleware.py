import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from core.logger import setup_logging

setup_logging()
api_logger = logging.getLogger("api")


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        body = b""
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            try:
                body = await request.body()
                request._receive = self._create_receive_with_body(body)
            except Exception:
                body = b"[UNREADABLE BODY]"

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        client = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path
        status_code = response.status_code
        body_str = body.decode("utf-8").replace("\n", " ") if body else "No body"

        api_logger.info(
            f"{client} | {method} {url} -> {status_code} | {process_time:.2f}ms | body={body_str}"
        )

        return response

    @staticmethod
    def _create_receive_with_body(body: bytes):
        async def receive():
            return {
                "type": "http.request",
                "body": body
            }

        return receive
