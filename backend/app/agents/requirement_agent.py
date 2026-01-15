"""Requirement Analysis Agent"""

import json
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent, ModelProvider
from app.services.knowledge_base import KnowledgeBaseService


class RequirementAgent(BaseAgent):
    """
    Agent for analyzing requirement documents and extracting test information.
    
    Extracts:
    - Function points
    - Business rules
    - Data models
    - API definitions
    - Test focus areas
    - Risk points
    """
    
    def __init__(
        self,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        knowledge_base_service: Optional[KnowledgeBaseService] = None
    ):
        """
        Initialize requirement analysis agent.
        
        Args:
            model_provider: LLM provider
            model_name: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            knowledge_base_service: Knowledge base service for retrieval
        """
        super().__init__(
            agent_type="requirement",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.kb_service = knowledge_base_service
    
    def build_prompt(
        self,
        requirement_text: str,
        test_type: str = "ui",
        knowledge_context: Optional[str] = None
    ) -> str:
        """
        Build prompt for requirement analysis.
        
        Args:
            requirement_text: Requirement document text
            test_type: Type of testing (ui/api/unit)
            knowledge_context: Retrieved knowledge base context
            
        Returns:
            Formatted prompt
        """
        test_type_guidance = {
            "ui": "重点关注用户界面交互、页面流程、用户体验、兼容性等方面",
            "api": "重点关注接口定义、参数校验、业务逻辑、异常处理、性能和安全等方面",
            "unit": "重点关注代码逻辑、分支覆盖、边界条件、异常处理等方面"
        }
        
        guidance = test_type_guidance.get(test_type, test_type_guidance["ui"])
        
        prompt = f"""你是一个专业的测试需求分析专家。请分析以下需求文档,提取测试相关的关键信息。

测试类型: {test_type}
分析重点: {guidance}

需求文档:
{requirement_text}
"""
        
        # Add knowledge base context if available
        if knowledge_context:
            prompt += f"""

参考历史知识:
{knowledge_context}
"""
        
        prompt += """

请按照以下JSON格式输出分析结果:
{
  "function_points": ["功能点1", "功能点2", ...],
  "business_rules": ["业务规则1", "业务规则2", ...],
  "data_models": [
    {
      "entity": "实体名称",
      "fields": ["字段1", "字段2", ...]
    }
  ],
  "api_definitions": [
    {
      "method": "HTTP方法",
      "url": "接口路径",
      "description": "接口描述"
    }
  ],
  "test_focus": ["测试重点1", "测试重点2", ...],
  "risk_points": ["风险点1", "风险点2", ...]
}

要求:
1. 提取所有关键功能点,确保完整性
2. 识别重要的业务规则和约束条件
3. 提取数据模型和字段信息
4. 如果是接口测试,提取所有API定义
5. 明确测试重点和优先级
6. 识别潜在的风险点和易错点
7. 输出必须是有效的JSON格式
8. 如果某个字段没有内容,使用空数组[]

请直接输出JSON,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured requirement analysis.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed requirement analysis dict
            
        Raises:
            ValueError: If response is not valid JSON
        """
        # Clean response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            result = json.loads(response)
            
            # Validate required fields
            required_fields = [
                "function_points",
                "business_rules",
                "data_models",
                "api_definitions",
                "test_focus",
                "risk_points"
            ]
            
            for field in required_fields:
                if field not in result:
                    result[field] = []
            
            # Validate data model structure
            if result["data_models"]:
                for model in result["data_models"]:
                    if "entity" not in model:
                        model["entity"] = "Unknown"
                    if "fields" not in model:
                        model["fields"] = []
            
            # Validate API definition structure
            if result["api_definitions"]:
                for api in result["api_definitions"]:
                    if "method" not in api:
                        api["method"] = "GET"
                    if "url" not in api:
                        api["url"] = ""
                    if "description" not in api:
                        api["description"] = ""
            
            return result
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")
    
    async def analyze(
        self,
        requirement_text: str,
        test_type: str = "ui",
        knowledge_context: Optional[str] = None,
        stream_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze requirement document.
        
        Args:
            requirement_text: Requirement document text
            test_type: Type of testing (ui/api/unit)
            knowledge_context: Knowledge base context string
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            Requirement analysis result
        """
        # Build prompt
        prompt = self.build_prompt(
            requirement_text=requirement_text,
            test_type=test_type,
            knowledge_context=knowledge_context
        )
        
        # Generate analysis
        system_message = "你是一个专业的测试需求分析专家,擅长从需求文档中提取测试相关信息。"
        
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
    
    def _extract_search_terms(self, text: str, max_terms: int = 10) -> str:
        """
        Extract key search terms from requirement text.
        
        Args:
            text: Requirement text
            max_terms: Maximum number of terms to extract
            
        Returns:
            Space-separated search terms
        """
        # Simple extraction - take first few meaningful words
        # In production, could use NLP for better term extraction
        words = text.split()
        
        # Filter out common words and take first max_terms
        stop_words = {"的", "是", "在", "和", "与", "或", "等", "及", "了", "着", "过"}
        terms = [w for w in words if len(w) > 1 and w not in stop_words][:max_terms]
        
        return " ".join(terms)
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate requirement analysis result.
        
        Args:
            result: Analysis result to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if result has minimum required content
        if not result.get("function_points"):
            return False
        
        if not result.get("test_focus"):
            return False
        
        return True
