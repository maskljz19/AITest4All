"""Scenario Generation Agent"""

import json
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent, ModelProvider


class ScenarioAgent(BaseAgent):
    """
    Agent for generating test scenarios based on requirement analysis.
    
    Generates scenarios for:
    - UI testing: normal, exception, boundary, compatibility, interaction
    - API testing: normal, validation, business logic, exception, security, performance
    - Unit testing: statement, branch, condition, path, exception coverage
    """
    
    def __init__(
        self,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 3000
    ):
        """
        Initialize scenario generation agent.
        
        Args:
            model_provider: LLM provider
            model_name: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(
            agent_type="scenario",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def _get_ui_test_prompt_template(self) -> str:
        """Get prompt template for UI testing scenarios"""
        return """
请为UI测试生成全面的测试场景,包括:

1. 正常场景(normal): 用户正常操作流程
2. 异常场景(exception): 错误输入、网络异常、权限不足等
3. 边界场景(boundary): 输入边界值、极限情况
4. 兼容性场景(compatibility): 不同浏览器、设备、分辨率
5. 交互场景(interaction): 多步骤操作、页面跳转、状态变化

每个场景应包含:
- scenario_id: 场景编号(如S001)
- name: 场景名称
- description: 场景描述
- precondition: 前置条件
- expected_result: 预期结果
- priority: 优先级(P0/P1/P2)
- category: 场景分类(normal/exception/boundary/compatibility/interaction)
"""
    
    def _get_api_test_prompt_template(self) -> str:
        """Get prompt template for API testing scenarios"""
        return """
请为接口测试生成全面的测试场景,包括:

1. 正常场景(normal): 正确参数调用,返回预期结果
2. 参数校验场景(validation): 必填参数缺失、参数类型错误、参数格式错误
3. 业务逻辑场景(business): 业务规则验证、状态流转、数据一致性
4. 异常场景(exception): 服务异常、超时、依赖服务失败
5. 安全场景(security): 权限验证、SQL注入、XSS攻击
6. 性能场景(performance): 并发请求、大数据量、响应时间

每个场景应包含:
- scenario_id: 场景编号(如S001)
- name: 场景名称
- description: 场景描述
- precondition: 前置条件
- expected_result: 预期结果
- priority: 优先级(P0/P1/P2)
- category: 场景分类(normal/validation/business/exception/security/performance)
"""
    
    def _get_unit_test_prompt_template(self) -> str:
        """Get prompt template for unit testing scenarios"""
        return """
请为白盒测试生成全面的测试场景,包括:

1. 语句覆盖(statement): 覆盖所有代码语句
2. 分支覆盖(branch): 覆盖所有if/else分支
3. 条件覆盖(condition): 覆盖所有条件组合
4. 路径覆盖(path): 覆盖所有执行路径
5. 异常覆盖(exception): 覆盖所有异常处理

每个场景应包含:
- scenario_id: 场景编号(如S001)
- name: 场景名称
- description: 场景描述
- precondition: 前置条件
- expected_result: 预期结果
- priority: 优先级(P0/P1/P2)
- category: 场景分类(statement/branch/condition/path/exception)
"""
    
    def build_prompt(
        self,
        requirement_analysis: Dict[str, Any],
        test_type: str = "ui",
        defect_history: Optional[str] = None
    ) -> str:
        """
        Build prompt for scenario generation.
        
        Args:
            requirement_analysis: Requirement analysis result
            test_type: Type of testing (ui/api/unit)
            defect_history: Historical defect information
            
        Returns:
            Formatted prompt
        """
        # Get test type specific template
        if test_type == "ui":
            template = self._get_ui_test_prompt_template()
        elif test_type == "api":
            template = self._get_api_test_prompt_template()
        elif test_type == "unit":
            template = self._get_unit_test_prompt_template()
        else:
            template = self._get_ui_test_prompt_template()
        
        prompt = f"""你是一个专业的测试场景设计专家。请根据需求分析结果生成全面的测试场景。

需求分析结果:
功能点: {json.dumps(requirement_analysis.get('function_points', []), ensure_ascii=False)}
业务规则: {json.dumps(requirement_analysis.get('business_rules', []), ensure_ascii=False)}
测试重点: {json.dumps(requirement_analysis.get('test_focus', []), ensure_ascii=False)}
风险点: {json.dumps(requirement_analysis.get('risk_points', []), ensure_ascii=False)}
"""
        
        if test_type == "api" and requirement_analysis.get('api_definitions'):
            prompt += f"\nAPI定义: {json.dumps(requirement_analysis['api_definitions'], ensure_ascii=False)}\n"
        
        if test_type == "ui" and requirement_analysis.get('data_models'):
            prompt += f"\n数据模型: {json.dumps(requirement_analysis['data_models'], ensure_ascii=False)}\n"
        
        prompt += template
        
        # Add defect history if available
        if defect_history:
            prompt += f"""

历史缺陷参考:
{defect_history}

请特别关注历史缺陷中出现的问题,确保生成相应的测试场景。
"""
        
        prompt += """

请按照以下JSON格式输出场景列表:
[
  {
    "scenario_id": "S001",
    "name": "场景名称",
    "description": "场景详细描述",
    "precondition": "前置条件",
    "expected_result": "预期结果",
    "priority": "P0",
    "category": "场景分类"
  }
]

要求:
1. 场景要全面,覆盖正常、异常、边界等各种情况
2. 场景描述要具体,避免模糊表述
3. 优先级要合理,P0为核心功能,P1为重要功能,P2为次要功能
4. 场景分类要准确
5. 输出必须是有效的JSON数组格式
6. 至少生成5个场景,最多20个场景

请直接输出JSON数组,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into scenario list.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of scenario dicts
            
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
            scenarios = json.loads(response)
            
            if not isinstance(scenarios, list):
                raise ValueError("Response must be a JSON array")
            
            # Validate and normalize each scenario
            for i, scenario in enumerate(scenarios):
                # Ensure required fields
                if "scenario_id" not in scenario:
                    scenario["scenario_id"] = f"S{i+1:03d}"
                if "name" not in scenario:
                    scenario["name"] = f"场景{i+1}"
                if "description" not in scenario:
                    scenario["description"] = ""
                if "precondition" not in scenario:
                    scenario["precondition"] = ""
                if "expected_result" not in scenario:
                    scenario["expected_result"] = ""
                if "priority" not in scenario:
                    scenario["priority"] = "P1"
                if "category" not in scenario:
                    scenario["category"] = "normal"
                
                # Validate priority
                if scenario["priority"] not in ["P0", "P1", "P2"]:
                    scenario["priority"] = "P1"
            
            return scenarios
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")
    
    async def generate(
        self,
        requirement_analysis: Dict[str, Any],
        test_type: str = "ui",
        defect_history: Optional[str] = None,
        stream_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate test scenarios.
        
        Args:
            requirement_analysis: Requirement analysis result
            test_type: Type of testing (ui/api/unit)
            defect_history: Defect history context string
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            List of test scenarios
        """
        # Build prompt
        prompt = self.build_prompt(
            requirement_analysis=requirement_analysis,
            test_type=test_type,
            defect_history=defect_history
        )
        
        system_message = "你是一个专业的测试场景设计专家,擅长设计全面的测试场景。"
        
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
    
    def classify_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Classify scenarios by category.
        
        Args:
            scenarios: List of scenarios
            
        Returns:
            Dict mapping category to list of scenarios
        """
        classified = {}
        
        for scenario in scenarios:
            category = scenario.get("category", "normal")
            if category not in classified:
                classified[category] = []
            classified[category].append(scenario)
        
        return classified
