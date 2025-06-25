"""Error handling middleware"""
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import traceback

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """Global error handler middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # Log the error
        logger.error(
            f"Unhandled error: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "client": request.client.host if request.client else None,
            }
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc) if logger.level <= logging.DEBUG else "An unexpected error occurred",
                "path": request.url.path,
            }
        )