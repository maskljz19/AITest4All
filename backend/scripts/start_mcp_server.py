"""Start MCP Server

独立启动 MCP Server，不影响主应用。

Usage:
    python scripts/start_mcp_server.py
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.mcp.server import TestKnowledgeMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function"""
    try:
        logger.info("Initializing Test Knowledge MCP Server...")
        server = TestKnowledgeMCPServer()
        
        logger.info("MCP Server is ready")
        logger.info("Available tools:")
        logger.info("  - search_test_cases: 搜索测试用例")
        logger.info("  - search_test_rules: 搜索测试规范")
        logger.info("  - search_defects: 搜索历史缺陷")
        logger.info("  - search_api_docs: 搜索 API 文档")
        
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by user")
    except Exception as e:
        logger.error(f"MCP Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
