"""MCP Server Implementation

提供测试知识库的 MCP 服务，让外部 AI 工具（Cursor、Windsurf 等）能够：
- 搜索测试用例知识库
- 查询测试规范文档
- 访问历史缺陷信息
"""

import logging
from typing import List, Dict, Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server

from app.core.database import get_async_session
from app.services.knowledge_base import KnowledgeBaseService
from app.tools import KnowledgeBaseTool, KnowledgeBaseSearchInput

logger = logging.getLogger(__name__)


class TestKnowledgeMCPServer:
    """测试知识库 MCP Server
    
    提供只读访问测试知识库的 MCP 服务。
    """
    
    def __init__(self):
        self.server = Server("test-knowledge-server")
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """注册 MCP 工具"""
        
        @self.server.list_tools()
        async def list_tools():
            """列出可用工具"""
            return [
                {
                    "name": "search_test_cases",
                    "description": "搜索测试用例知识库，查找相关的测试用例、测试场景和测试方法",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询文本"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "search_test_rules",
                    "description": "搜索测试规范和测试标准，查找测试方法论、最佳实践和规范文档",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询文本"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "search_defects",
                    "description": "搜索历史缺陷记录，查找类似的 bug、问题模式和解决方案",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询文本"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "search_api_docs",
                    "description": "搜索 API 文档，查找接口定义、参数说明和使用示例",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询文本"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]):
            """调用工具"""
            try:
                if name == "search_test_cases":
                    return await self._search_knowledge_base(
                        query=arguments["query"],
                        kb_type="case",
                        limit=arguments.get("limit", 5)
                    )
                elif name == "search_test_rules":
                    return await self._search_knowledge_base(
                        query=arguments["query"],
                        kb_type="rule",
                        limit=arguments.get("limit", 5)
                    )
                elif name == "search_defects":
                    return await self._search_knowledge_base(
                        query=arguments["query"],
                        kb_type="defect",
                        limit=arguments.get("limit", 5)
                    )
                elif name == "search_api_docs":
                    return await self._search_knowledge_base(
                        query=arguments["query"],
                        kb_type="api",
                        limit=arguments.get("limit", 5)
                    )
                else:
                    return {
                        "error": f"Unknown tool: {name}"
                    }
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return {
                    "error": str(e)
                }
    
    def _register_resources(self):
        """注册 MCP 资源"""
        
        @self.server.list_resources()
        async def list_resources():
            """列出可用资源"""
            return [
                {
                    "uri": "test-knowledge://stats",
                    "name": "知识库统计",
                    "description": "测试知识库的统计信息",
                    "mimeType": "application/json"
                }
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str):
            """读取资源"""
            if uri == "test-knowledge://stats":
                return await self._get_knowledge_base_stats()
            else:
                return {
                    "error": f"Unknown resource: {uri}"
                }
    
    async def _search_knowledge_base(
        self,
        query: str,
        kb_type: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索知识库
        
        Args:
            query: 搜索查询
            kb_type: 知识库类型
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            async with get_async_session() as db:
                kb_service = KnowledgeBaseService(db)
                results = await kb_service.search(
                    query=query,
                    kb_type=kb_type,
                    limit=limit
                )
                
                # 格式化结果
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "id": result.get("id"),
                        "name": result.get("name"),
                        "type": result.get("type"),
                        "content": result.get("content"),
                        "relevance": result.get("relevance"),
                        "created_at": result.get("created_at")
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Knowledge base search error: {e}")
            return []
    
    async def _get_knowledge_base_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息
        
        Returns:
            统计信息
        """
        try:
            async with get_async_session() as db:
                kb_service = KnowledgeBaseService(db)
                
                # 获取各类型文档数量
                stats = {
                    "total": 0,
                    "by_type": {}
                }
                
                for kb_type in ["case", "rule", "defect", "api"]:
                    docs = await kb_service.list_by_type(kb_type, limit=1000)
                    count = len(docs)
                    stats["by_type"][kb_type] = count
                    stats["total"] += count
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                "error": str(e)
            }
    
    async def run(self):
        """运行 MCP Server"""
        logger.info("Starting Test Knowledge MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """主函数"""
    server = TestKnowledgeMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
