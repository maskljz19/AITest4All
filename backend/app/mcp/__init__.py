"""MCP (Model Context Protocol) Server

对外提供 MCP 服务，让其他 AI 工具能够访问测试知识库。
"""

from app.mcp.server import TestKnowledgeMCPServer

__all__ = ["TestKnowledgeMCPServer"]
