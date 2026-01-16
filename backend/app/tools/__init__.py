"""Tool Abstraction Layer

统一的工具接口，用于 Agent 访问外部能力。
"""

from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.tools.knowledge_base import KnowledgeBaseTool, KnowledgeBaseSearchInput
from app.tools.script_executor import ScriptExecutorTool, ScriptExecuteInput
from app.tools.document_parser import DocumentParserTool, DocumentParseInput

__all__ = [
    "BaseTool",
    "ToolInput",
    "ToolOutput",
    "KnowledgeBaseTool",
    "KnowledgeBaseSearchInput",
    "ScriptExecutorTool",
    "ScriptExecuteInput",
    "DocumentParserTool",
    "DocumentParseInput",
]
