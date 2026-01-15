"""API Routes"""

from app.api.generate import router as generate_router
from app.api.websocket import router as websocket_router

__all__ = [
    "generate_router",
    "websocket_router",
]
