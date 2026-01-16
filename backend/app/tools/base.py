"""Base Tool Interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class ToolInput(BaseModel):
    """Tool 输入参数基类"""
    pass


class ToolOutput(BaseModel):
    """Tool 输出结果基类"""
    pass


class BaseTool(ABC):
    """工具基类
    
    所有工具必须实现此接口，提供统一的调用方式。
    """
    
    name: str
    description: str
    
    @property
    @abstractmethod
    def input_schema(self) -> type[ToolInput]:
        """输入参数 Schema"""
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> type[ToolOutput]:
        """输出结果 Schema"""
        pass
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """执行工具
        
        Args:
            input_data: 输入参数
            
        Returns:
            执行结果
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的 JSON Schema
        
        Returns:
            包含工具名称、描述和参数 Schema 的字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.schema(),
            "output_schema": self.output_schema.schema(),
        }
    
    def to_mcp_tool(self) -> Dict[str, Any]:
        """转换为 MCP Tool 格式
        
        用于 MCP Server 注册工具。
        
        Returns:
            MCP Tool 定义
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema.schema()
        }
