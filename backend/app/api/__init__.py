"""API Routes"""

from app.api.generate import router as generate_router
from app.api.websocket import router as websocket_router
from app.api.prompts import router as prompts_router
from app.api.model_config import router as model_config_router
from app.api.feedback import router as feedback_router

__all__ = [
    "generate_router",
    "websocket_router",
    "prompts_router",
    "model_config_router",
    "feedback_router",
]
