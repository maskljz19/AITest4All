"""Document Parser Tool"""

from typing import Optional
from pydantic import Field

from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.services.document_parser import DocumentParser


class DocumentParseInput(ToolInput):
    """文档解析输入"""
    content: Optional[bytes] = Field(None, description="文档内容（二进制）")
    filename: Optional[str] = Field(None, description="文件名")
    url: Optional[str] = Field(None, description="URL 地址")


class DocumentParseOutput(ToolOutput):
    """文档解析输出"""
    text: str = Field(..., description="解析后的文本内容")
    metadata: dict = Field(default_factory=dict, description="文档元数据")


class DocumentParserTool(BaseTool):
    """文档解析工具
    
    用于解析各种格式的文档（Word、PDF、Markdown、Excel、TXT）或抓取 URL 内容。
    """
    
    name = "document_parser"
    description = "解析文档（Word/PDF/Markdown/Excel/TXT）或抓取 URL 内容"
    
    def __init__(self, parser: DocumentParser):
        self.parser = parser
    
    @property
    def input_schema(self) -> type[ToolInput]:
        return DocumentParseInput
    
    @property
    def output_schema(self) -> type[ToolOutput]:
        return DocumentParseOutput
    
    async def execute(self, input_data: DocumentParseInput) -> DocumentParseOutput:
        """执行文档解析
        
        Args:
            input_data: 解析参数
            
        Returns:
            解析结果
        """
        if input_data.url:
            # 解析 URL
            text = self.parser.parse_url(input_data.url)
            metadata = {"source": "url", "url": input_data.url}
        elif input_data.content and input_data.filename:
            # 解析文件
            text = self.parser.extract_text(input_data.content, input_data.filename)
            metadata = {"source": "file", "filename": input_data.filename}
        else:
            raise ValueError("Must provide either url or (content + filename)")
        
        return DocumentParseOutput(
            text=text,
            metadata=metadata
        )
