"""Database Connection Management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Convert postgresql:// to postgresql+asyncpg://
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with security configurations
engine = create_async_engine(
    database_url,
    echo=settings.app_env == "development",
    pool_size=20,  # Maximum connections in pool
    max_overflow=10,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database connection"""
    # Import all models here to ensure they are registered
    from app.models import (
        AgentConfig,
        KnowledgeBase,
        PythonScript,
        CaseTemplate,
        TestCase,
    )
    
    # Initialize database security measures
    from app.core.database_security import setup_database_security
    setup_database_security()
    
    logger.info("Database initialized with security measures")


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logger.info("Database connection closed")


async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_async_session():
    """Get async session context manager for non-dependency usage"""
    return AsyncSessionLocal()
