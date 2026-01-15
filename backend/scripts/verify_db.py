"""Database Verification Script

This script verifies that the database is properly set up with all tables and seed data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal
from app.core.config import settings


async def verify_database():
    """Verify database setup"""
    print("🔍 Verifying database setup...")
    print(f"📍 Database URL: {settings.database_url}")
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if tables exist
            print("\n📋 Checking tables...")
            tables = [
                'agent_configs',
                'knowledge_bases',
                'python_scripts',
                'case_templates',
                'test_cases'
            ]
            
            for table in tables:
                result = await session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )
                count = result.scalar()
                print(f"  ✅ {table}: {count} rows")
            
            # Check builtin scripts
            print("\n🔧 Checking builtin scripts...")
            result = await session.execute(
                text("SELECT name FROM python_scripts WHERE is_builtin = true ORDER BY name")
            )
            scripts = result.fetchall()
            if scripts:
                for script in scripts:
                    print(f"  ✅ {script[0]}")
            else:
                print("  ⚠️  No builtin scripts found")
            
            # Check default agent configs
            print("\n🤖 Checking default agent configurations...")
            result = await session.execute(
                text("SELECT agent_type, agent_name FROM agent_configs WHERE is_default = true ORDER BY agent_type")
            )
            configs = result.fetchall()
            if configs:
                for config in configs:
                    print(f"  ✅ {config[0]}: {config[1]}")
            else:
                print("  ⚠️  No default agent configs found")
            
            # Check full-text search setup
            print("\n🔎 Checking full-text search setup...")
            result = await session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM pg_indexes 
                    WHERE tablename = 'knowledge_bases' 
                    AND indexname = 'idx_knowledge_search'
                """)
            )
            index_count = result.scalar()
            if index_count > 0:
                print("  ✅ Full-text search index exists")
            else:
                print("  ⚠️  Full-text search index not found")
            
            # Check trigger
            result = await session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM pg_trigger 
                    WHERE tgname = 'tsvector_update'
                """)
            )
            trigger_count = result.scalar()
            if trigger_count > 0:
                print("  ✅ Auto-update trigger exists")
            else:
                print("  ⚠️  Auto-update trigger not found")
            
            print("\n✅ Database verification completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Database verification failed: {e}")
        return False


async def test_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def main():
    """Main verification function"""
    print("=" * 60)
    print("Database Verification Tool")
    print("=" * 60)
    
    # Test connection
    if not await test_connection():
        sys.exit(1)
    
    print()
    
    # Verify database
    if not await verify_database():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("All checks passed! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
