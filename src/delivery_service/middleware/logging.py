import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from loguru import logger


async def response_time(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.monotonic()

    response = await call_next(request)

    duration_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        "HTTP request | duration_ms={} | method={} | path={} | status_code={}",
        round(duration_ms, 2),
        request.method,
        request.url.path,
        response.status_code,
    )

    return response
