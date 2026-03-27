from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

log = structlog.get_logger()

async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=repr(exc),
        exc_info=True,
    )
    # Never leak stack traces to the user
    return JSONResponse(status_code=500, content={
        "error": "An unexpected error occurred. Please try again.",
        "request_id": request.headers.get("x-request-id"),
    })
