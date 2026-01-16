"""Script Executor Tool"""

from typing import Dict, Any, Optional
from pydantic import Field

from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.services.script_executor import ScriptExecutor


class ScriptExecuteInput(ToolInput):
    """脚本执行输入"""
    script_code: str = Field(..., description="Python 脚本代码")
    params: Dict[str, Any] = Field(default_factory=dict, description="脚本参数")
    timeout: int = Field(30, description="超时时间（秒）", ge=1, le=60)


class ScriptExecuteOutput(ToolOutput):
    """脚本执行输出"""
    success: bool = Field(..., description="是否执行成功")
    result: Optional[Any] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间（秒）")


class ScriptExecutorTool(BaseTool):
    """脚本执行工具
    
    用于执行 Python 脚本生成测试数据（如手机号、邮箱、时间戳等）。
    """
    
    name = "script_executor"
    description = "执行 Python 脚本生成测试数据，如手机号、邮箱、时间戳、MD5 等"
    
    def __init__(self, executor: ScriptExecutor):
        self.executor = executor
    
    @property
    def input_schema(self) -> type[ToolInput]:
        return ScriptExecuteInput
    
    @property
    def output_schema(self) -> type[ToolOutput]:
        return ScriptExecuteOutput
    
    async def execute(self, input_data: ScriptExecuteInput) -> ScriptExecuteOutput:
        """执行脚本
        
        Args:
            input_data: 脚本执行参数
            
        Returns:
            执行结果
        """
        result = await self.executor.execute(
            script_code=input_data.script_code,
            params=input_data.params,
            timeout=input_data.timeout
        )
        
        return ScriptExecuteOutput(
            success=result.get("success", False),
            result=result.get("result"),
            error=result.get("error"),
            execution_time=result.get("execution_time", 0.0)
        )
