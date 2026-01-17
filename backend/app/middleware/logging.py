"""Custom logging middleware to filter health check logs"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class HealthCheckFilter(logging.Filter):
    """Filter to exclude health check endpoint logs"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Filter out health check requests
        message = record.getMessage()
        return '/health' not in message and 'GET /health' not in message


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to suppress health check logs"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for health check endpoint
        if request.url.path == '/health':
            return await call_next(request)
        
        # Process other requests normally
        response = await call_next(request)
        return response


def setup_logging_filters():
    """Setup logging filters to exclude health check logs"""
    # Get uvicorn access logger
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.addFilter(HealthCheckFilter())
    
    # Get uvicorn error logger
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.addFilter(HealthCheckFilter())
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.addFilter(HealthCheckFilter())
