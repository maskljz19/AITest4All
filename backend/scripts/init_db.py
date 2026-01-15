"""Database Initialization Script

This script initializes the database by running Alembic migrations.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.core.database import engine, Base


async def init_database():
    """Initialize database with tables and seed data"""
    print("🚀 Starting database initialization...")
    
    # Run Alembic migrations
    print("📦 Running Alembic migrations...")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    
    try:
        # Upgrade to latest version
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    
    print("✅ Database initialization completed!")


if __name__ == "__main__":
    asyncio.run(init_database())
