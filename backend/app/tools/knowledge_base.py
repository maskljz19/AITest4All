"""Knowledge Base Tool"""

from typing import List, Dict, Any, Optional
from pydantic import Field

from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.services.knowledge_base import KnowledgeBaseService


class KnowledgeBaseSearchInput(ToolInput):
    """知识库搜索输入"""
    query: str = Field(..., description="搜索查询文本")
    kb_type: Optional[str] = Field(None, description="知识库类型 (case/defect/rule/api)")
    limit: int = Field(5, description="返回结果数量限制", ge=1, le=20)


class KnowledgeBaseSearchOutput(ToolOutput):
    """知识库搜索输出"""
    results: List[Dict[str, Any]] = Field(..., description="搜索结果列表")
    count: int = Field(..., description="结果数量")


class KnowledgeBaseTool(BaseTool):
    """知识库搜索工具
    
    用于搜索知识库获取相关文档、历史案例、测试规范等。
    """
    
    name = "knowledge_base_search"
    description = "搜索知识库获取相关文档、历史案例、测试规范和 API 文档"
    
    def __init__(self, kb_service: KnowledgeBaseService):
        self.kb_service = kb_service
    
    @property
    def input_schema(self) -> type[ToolInput]:
        return KnowledgeBaseSearchInput
    
    @property
    def output_schema(self) -> type[ToolOutput]:
        return KnowledgeBaseSearchOutput
    
    async def execute(self, input_data: KnowledgeBaseSearchInput) -> KnowledgeBaseSearchOutput:
        """执行知识库搜索
        
        Args:
            input_data: 搜索参数
            
        Returns:
            搜索结果
        """
        results = await self.kb_service.search(
            query=input_data.query,
            kb_type=input_data.kb_type,
            limit=input_data.limit
        )
        
        return KnowledgeBaseSearchOutput(
            results=results,
            count=len(results)
        )
