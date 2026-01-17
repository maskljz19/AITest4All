"""FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.core.exceptions import AppException
from app.core.error_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.middleware import LoggingMiddleware, setup_logging_filters
from app.api import generate_router, websocket_router, prompts_router, model_config_router, feedback_router
from app.api.knowledge_base import router as knowledge_base_router
from app.api.scripts import router as scripts_router
from app.api.agent_configs import router as agent_configs_router
from app.api.templates import router as templates_router
from app.api.export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    await init_redis()
    # Setup logging filters
    setup_logging_filters()
    yield
    # Shutdown
    await close_db()
    await close_redis()


app = FastAPI(
    title="AI Test Case Generator",
    description="AI-driven intelligent test case generation system",
    version="0.1.0",
    lifespan=lifespan
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS middleware - configurable via environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware to filter health check logs
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(generate_router)
app.include_router(websocket_router)
app.include_router(knowledge_base_router)
app.include_router(scripts_router)
app.include_router(agent_configs_router)
app.include_router(templates_router)
app.include_router(export_router)
app.include_router(prompts_router)
app.include_router(model_config_router)
app.include_router(feedback_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Test Case Generator API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
