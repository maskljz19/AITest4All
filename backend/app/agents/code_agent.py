"""Code Generation Agent"""

import json
import re
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent, ModelProvider


class CodeAgent(BaseAgent):
    """
    Agent for generating automated test code from test cases.
    
    Supports:
    - UI testing: Pytest + Selenium
    - API testing: Pytest + Requests
    - Unit testing: Pytest
    """
    
    # Default tech stacks
    DEFAULT_TECH_STACKS = {
        "ui": {
            "framework": "Pytest + Selenium",
            "description": "使用Pytest测试框架和Selenium进行UI自动化测试,采用Page Object Model设计模式"
        },
        "api": {
            "framework": "Pytest + Requests",
            "description": "使用Pytest测试框架和Requests库进行接口自动化测试"
        },
        "unit": {
            "framework": "Pytest",
            "description": "使用Pytest测试框架进行单元测试"
        }
    }
    
    def __init__(
        self,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.3,  # Lower temperature for code generation
        max_tokens: int = 4000
    ):
        """
        Initialize code generation agent.
        
        Args:
            model_provider: LLM provider
            model_name: Model name
            temperature: Sampling temperature (lower for code)
            max_tokens: Maximum tokens
        """
        super().__init__(
            agent_type="code",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def _get_ui_test_template(self) -> str:
        """Get template for UI test code generation"""
        return """
生成UI自动化测试代码,要求:

1. 使用Pytest框架
2. 使用Selenium WebDriver
3. 采用Page Object Model设计模式
4. 包含以下文件:
   - test_*.py: 测试用例文件
   - pages/*.py: 页面对象文件
   - conftest.py: Pytest配置和fixtures
   - requirements.txt: 依赖包列表
   - README.md: 使用说明

5. 代码规范:
   - 使用类型注解
   - 添加必要的注释
   - 使用有意义的变量名
   - 遵循PEP 8规范

6. 测试用例要包含:
   - 清晰的测试方法名
   - 详细的断言
   - 适当的等待机制
   - 错误处理
"""
    
    def _get_api_test_template(self) -> str:
        """Get template for API test code generation"""
        return """
生成接口自动化测试代码,要求:

1. 使用Pytest框架
2. 使用Requests库
3. 包含以下文件:
   - test_*.py: 测试用例文件
   - conftest.py: Pytest配置和fixtures
   - config.py: 配置文件(base_url等)
   - requirements.txt: 依赖包列表
   - README.md: 使用说明

4. 代码规范:
   - 使用类型注解
   - 添加必要的注释
   - 使用有意义的变量名
   - 遵循PEP 8规范

5. 测试用例要包含:
   - 清晰的测试方法名
   - 完整的请求参数
   - 详细的响应断言
   - 状态码验证
   - 错误处理
"""
    
    def _get_unit_test_template(self) -> str:
        """Get template for unit test code generation"""
        return """
生成单元测试代码,要求:

1. 使用Pytest框架
2. 包含以下文件:
   - test_*.py: 测试用例文件
   - conftest.py: Pytest配置和fixtures
   - requirements.txt: 依赖包列表
   - README.md: 使用说明

3. 代码规范:
   - 使用类型注解
   - 添加必要的注释
   - 使用有意义的变量名
   - 遵循PEP 8规范

4. 测试用例要包含:
   - 清晰的测试方法名
   - 完整的测试数据
   - 详细的断言
   - Mock对象(如需要)
   - 边界条件测试
"""
    
    def build_prompt(
        self,
        test_cases: List[Dict[str, Any]],
        tech_stack: Optional[str] = None,
        use_default_stack: bool = True
    ) -> str:
        """
        Build prompt for code generation.
        
        Args:
            test_cases: List of test cases
            tech_stack: Custom tech stack description
            use_default_stack: Whether to use default tech stack
            
        Returns:
            Formatted prompt
        """
        # Determine test type from first test case
        test_type = test_cases[0].get("test_type", "ui") if test_cases else "ui"
        
        # Get tech stack description
        if use_default_stack:
            stack_info = self.DEFAULT_TECH_STACKS.get(test_type, self.DEFAULT_TECH_STACKS["ui"])
            tech_stack_desc = f"{stack_info['framework']}\n{stack_info['description']}"
        else:
            tech_stack_desc = tech_stack or "请根据测试用例选择合适的技术栈"
        
        # Get template
        if test_type == "ui":
            template = self._get_ui_test_template()
        elif test_type == "api":
            template = self._get_api_test_template()
        else:
            template = self._get_unit_test_template()
        
        prompt = f"""你是一个专业的测试开发工程师。请根据测试用例生成自动化测试代码。

技术栈:
{tech_stack_desc}

测试用例:
{json.dumps(test_cases, ensure_ascii=False, indent=2)}

{template}

请按照以下JSON格式输出代码文件:
{{
  "files": {{
    "test_example.py": "# 测试代码内容",
    "conftest.py": "# Pytest配置",
    "requirements.txt": "# 依赖包列表",
    "README.md": "# 使用说明"
  }}
}}

要求:
1. 代码要完整可运行
2. 包含所有必要的导入语句
3. 代码要有良好的结构和注释
4. 测试用例要覆盖所有输入的测试场景
5. 依赖包要指定版本号
6. README要包含环境配置和运行说明
7. 输出必须是有效的JSON格式
8. 文件内容中的换行符使用\\n表示

请直接输出JSON,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def parse_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """
        Parse LLM response into code files.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dict with 'files' key containing filename -> content mapping
            
        Raises:
            ValueError: If response is not valid JSON
        """
        # Clean response - remove markdown code blocks if present
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Try to find JSON object in response
        # Sometimes LLM adds text before or after JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            response = json_match.group(0)
        
        try:
            result = json.loads(response)
            
            # Handle different response formats
            if "files" in result:
                files = result["files"]
            elif isinstance(result, dict) and all(isinstance(v, str) for v in result.values()):
                # Response is already in files format
                files = result
                result = {"files": files}
            else:
                raise ValueError("Response must contain 'files' key or be a dict of filename -> content")
            
            if not isinstance(files, dict):
                raise ValueError("'files' must be a dictionary")
            
            # Ensure at least one file
            if not files:
                raise ValueError("No files generated")
            
            return result
        
        except json.JSONDecodeError as e:
            # Try to fix common JSON errors
            try:
                # Fix trailing commas
                fixed_response = re.sub(r',(\s*[}\]])', r'\1', response)
                # Fix unescaped quotes in strings
                # This is a simplified fix - may not work for all cases
                result = json.loads(fixed_response)
                
                if "files" in result:
                    return result
                elif isinstance(result, dict):
                    return {"files": result}
                else:
                    raise ValueError("Invalid response format")
                    
            except:
                # If all fixes fail, provide detailed error
                error_msg = f"Failed to parse JSON response: {str(e)}"
                # Show first 500 chars of response for debugging
                preview = response[:500] + "..." if len(response) > 500 else response
                raise ValueError(f"{error_msg}\n\nResponse preview:\n{preview}")
    
    async def generate_code(
        self,
        test_cases: List[Dict[str, Any]],
        tech_stack: Optional[str] = None,
        use_default_stack: bool = True,
        stream: bool = False
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate test code from test cases.
        
        Args:
            test_cases: List of test cases
            tech_stack: Custom tech stack description
            use_default_stack: Whether to use default tech stack
            stream: Whether to stream response
            
        Returns:
            Dict with generated code files
        """
        if not test_cases:
            raise ValueError("No test cases provided")
        
        system_message = "你是一个专业的测试开发工程师,擅长编写高质量的自动化测试代码。"
        
        return await self.generate(
            stream=stream,
            system_message=system_message,
            test_cases=test_cases,
            tech_stack=tech_stack,
            use_default_stack=use_default_stack
        )
    
    def format_code(self, code: str, language: str = "python") -> str:
        """
        Format code for better readability.
        
        Args:
            code: Code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        if language == "python":
            # Basic Python formatting
            # Remove excessive blank lines
            code = re.sub(r'\n{3,}', '\n\n', code)
            
            # Ensure proper spacing around operators
            # This is a simplified version - in production use black or autopep8
            return code.strip()
        
        return code
    
    def extract_file_structure(self, files: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Extract file structure for display.
        
        Args:
            files: Dict of filename -> content
            
        Returns:
            Dict with directory structure
        """
        structure = {
            "root": [],
            "directories": {}
        }
        
        for filename in files.keys():
            if "/" in filename:
                # File in subdirectory
                parts = filename.split("/")
                directory = parts[0]
                file = "/".join(parts[1:])
                
                if directory not in structure["directories"]:
                    structure["directories"][directory] = []
                structure["directories"][directory].append(file)
            else:
                # File in root
                structure["root"].append(filename)
        
        return structure
    
    def get_default_tech_stack(self, test_type: str) -> Dict[str, str]:
        """
        Get default tech stack for test type.
        
        Args:
            test_type: Type of testing (ui/api/unit)
            
        Returns:
            Tech stack info dict
        """
        return self.DEFAULT_TECH_STACKS.get(test_type, self.DEFAULT_TECH_STACKS["ui"])


    async def generate(
        self,
        test_cases: List[Dict[str, Any]],
        tech_stack: Optional[str] = None,
        use_default_stack: bool = True,
        stream_callback: Optional[callable] = None
    ) -> Dict[str, str]:
        """
        Generate automated test code with optional streaming.
        
        Args:
            test_cases: List of test cases
            tech_stack: Custom tech stack description
            use_default_stack: Whether to use default tech stack
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            Dict with 'files' key containing filename -> code mapping
        """
        # Build prompt
        prompt = self.build_prompt(
            test_cases=test_cases,
            tech_stack=tech_stack,
            use_default_stack=use_default_stack
        )
        
        system_message = "你是一个专业的自动化测试代码生成专家,擅长编写高质量的测试代码。"
        
        if stream_callback:
            # Stream response
            response_text = ""
            stream = await self._call_llm_with_retry(
                prompt=prompt,
                system_message=system_message,
                stream=True
            )
            async for chunk in stream:
                response_text += chunk
                await stream_callback(chunk)
            
            return self.parse_response(response_text)
        else:
            # Non-streaming response
            response = await self._call_llm_with_retry(
                prompt=prompt,
                system_message=system_message,
                stream=False
            )
            return self.parse_response(response)
