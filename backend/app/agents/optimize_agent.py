"""Optimization and Supplement Agent"""

import json
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent, ModelProvider


class OptimizeAgent(BaseAgent):
    """
    Agent for optimizing and supplementing test cases based on user instructions.
    
    Supports:
    - Optimizing selected test cases
    - Supplementing new test cases
    - Conversational refinement
    """
    
    def __init__(
        self,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 3000
    ):
        """
        Initialize optimization agent.
        
        Args:
            model_provider: LLM provider
            model_name: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(
            agent_type="optimize",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def build_prompt(
        self,
        operation: str,
        instruction: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build prompt for optimization or supplement.
        
        Args:
            operation: Operation type ('optimize' or 'supplement')
            instruction: User instruction
            context: Context data (selected cases, requirement, etc.)
            
        Returns:
            Formatted prompt
        """
        if operation == "optimize":
            return self._build_optimize_prompt(instruction, context)
        elif operation == "supplement":
            return self._build_supplement_prompt(instruction, context)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _build_optimize_prompt(self, instruction: str, context: Dict[str, Any]) -> str:
        """Build prompt for optimizing test cases"""
        selected_cases = context.get("selected_cases", [])
        
        prompt = f"""你是一个专业的测试用例优化专家。请根据用户的指令优化选中的测试用例。

用户指令:
{instruction}

选中的测试用例:
{json.dumps(selected_cases, ensure_ascii=False, indent=2)}
"""
        
        # Add requirement context if available
        if context.get("requirement_analysis"):
            prompt += f"""

需求分析参考:
{json.dumps(context['requirement_analysis'], ensure_ascii=False, indent=2)}
"""
        
        prompt += """

请根据用户指令优化测试用例,可能的优化方向包括:
1. 细化测试步骤,使其更具体
2. 补充测试数据,使其更完整
3. 优化预期结果,使其更明确
4. 调整优先级
5. 改进用例描述
6. 添加边界条件测试
7. 增强错误处理验证

请按照以下JSON格式输出优化后的测试用例:
[
  {
    "case_id": "TC001",
    "title": "优化后的标题",
    "test_type": "ui/api/unit",
    "priority": "P0/P1/P2",
    "precondition": "前置条件",
    "steps": [
      {
        "step_no": 1,
        "action": "操作描述",
        "data": "测试数据",
        "expected": "预期结果"
      }
    ],
    "test_data": {},
    "expected_result": "整体预期结果",
    "postcondition": "后置条件",
    "optimization_notes": "优化说明"
  }
]

要求:
1. 保持原有用例的case_id
2. 根据用户指令进行针对性优化
3. 优化后的用例要更加完善
4. 添加optimization_notes字段说明优化内容
5. 输出必须是有效的JSON数组格式

请直接输出JSON数组,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def _build_supplement_prompt(self, instruction: str, context: Dict[str, Any]) -> str:
        """Build prompt for supplementing test cases"""
        existing_cases = context.get("existing_cases", [])
        requirement_analysis = context.get("requirement_analysis", {})
        
        prompt = f"""你是一个专业的测试用例设计专家。请根据用户的指令补充新的测试用例。

用户指令:
{instruction}

现有测试用例:
{json.dumps(existing_cases, ensure_ascii=False, indent=2)}

需求分析:
{json.dumps(requirement_analysis, ensure_ascii=False, indent=2)}
"""
        
        prompt += """

请根据用户指令补充新的测试用例,可能的补充方向包括:
1. 补充缺失的测试场景
2. 增加边界条件测试
3. 添加异常情况测试
4. 补充性能测试场景
5. 增加安全测试场景
6. 添加兼容性测试
7. 补充集成测试场景

请按照以下JSON格式输出新增的测试用例:
[
  {
    "case_id": "TC_NEW_001",
    "title": "新用例标题",
    "test_type": "ui/api/unit",
    "priority": "P0/P1/P2",
    "precondition": "前置条件",
    "steps": [
      {
        "step_no": 1,
        "action": "操作描述",
        "data": "测试数据",
        "expected": "预期结果"
      }
    ],
    "test_data": {},
    "expected_result": "整体预期结果",
    "postcondition": "后置条件",
    "supplement_reason": "补充原因"
  }
]

要求:
1. 新用例的case_id使用TC_NEW_前缀
2. 根据用户指令进行针对性补充
3. 避免与现有用例重复
4. 添加supplement_reason字段说明补充原因
5. 输出必须是有效的JSON数组格式
6. 至少补充1个用例,最多补充5个用例

请直接输出JSON数组,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into test case list.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of test case dicts
            
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
            cases = json.loads(response)
            
            if not isinstance(cases, list):
                raise ValueError("Response must be a JSON array")
            
            # Validate each case
            for case in cases:
                if "case_id" not in case:
                    case["case_id"] = "TC_UNKNOWN"
                if "title" not in case:
                    case["title"] = "未命名用例"
                if "test_type" not in case:
                    case["test_type"] = "ui"
                if "priority" not in case:
                    case["priority"] = "P1"
                if "steps" not in case:
                    case["steps"] = []
                if "test_data" not in case:
                    case["test_data"] = {}
                if "expected_result" not in case:
                    case["expected_result"] = ""
            
            return cases
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")
    
    async def optimize_cases(
        self,
        selected_cases: List[Dict[str, Any]],
        instruction: str,
        requirement_analysis: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Optimize selected test cases based on user instruction.
        
        Args:
            selected_cases: List of selected test cases to optimize
            instruction: User optimization instruction
            requirement_analysis: Optional requirement analysis for context
            stream: Whether to stream response
            
        Returns:
            List of optimized test cases
        """
        context = {
            "selected_cases": selected_cases,
            "requirement_analysis": requirement_analysis
        }
        
        system_message = "你是一个专业的测试用例优化专家,擅长根据用户需求改进测试用例。"
        
        return await self.generate(
            stream=stream,
            system_message=system_message,
            operation="optimize",
            instruction=instruction,
            context=context
        )
    
    async def supplement_cases(
        self,
        existing_cases: List[Dict[str, Any]],
        instruction: str,
        requirement_analysis: Dict[str, Any],
        stream: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Supplement new test cases based on user instruction.
        
        Args:
            existing_cases: List of existing test cases
            instruction: User supplement instruction
            requirement_analysis: Requirement analysis for context
            stream: Whether to stream response
            
        Returns:
            List of new test cases
        """
        context = {
            "existing_cases": existing_cases,
            "requirement_analysis": requirement_analysis
        }
        
        system_message = "你是一个专业的测试用例设计专家,擅长根据需求补充测试场景。"
        
        return await self.generate(
            stream=stream,
            system_message=system_message,
            operation="supplement",
            instruction=instruction,
            context=context
        )
    
    def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Parse user instruction to understand intent.
        
        Args:
            instruction: User instruction text
            
        Returns:
            Dict with parsed intent and parameters
        """
        instruction_lower = instruction.lower()
        
        # Detect operation type
        optimize_keywords = ["优化", "改进", "完善", "细化", "修改"]
        supplement_keywords = ["补充", "增加", "添加", "新增"]
        
        operation = "optimize"
        for keyword in supplement_keywords:
            if keyword in instruction_lower:
                operation = "supplement"
                break
        
        # Detect focus areas
        focus_areas = []
        if "步骤" in instruction_lower or "操作" in instruction_lower:
            focus_areas.append("steps")
        if "数据" in instruction_lower:
            focus_areas.append("test_data")
        if "预期" in instruction_lower or "结果" in instruction_lower:
            focus_areas.append("expected_result")
        if "边界" in instruction_lower:
            focus_areas.append("boundary")
        if "异常" in instruction_lower or "错误" in instruction_lower:
            focus_areas.append("exception")
        if "性能" in instruction_lower:
            focus_areas.append("performance")
        if "安全" in instruction_lower:
            focus_areas.append("security")
        
        return {
            "operation": operation,
            "focus_areas": focus_areas,
            "original_instruction": instruction
        }


    async def optimize(
        self,
        selected_cases: List[Dict[str, Any]],
        instruction: str,
        stream_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Optimize test cases with optional streaming.
        
        Args:
            selected_cases: Selected test cases to optimize
            instruction: Optimization instruction
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            Optimized test cases
        """
        # Build prompt
        prompt = self.build_optimize_prompt(
            selected_cases=selected_cases,
            instruction=instruction
        )
        
        system_message = "你是一个专业的测试用例优化专家,擅长根据用户需求改进测试用例。"
        
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
    
    async def supplement(
        self,
        existing_cases: List[Dict[str, Any]],
        requirement: str,
        stream_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Supplement new test cases with optional streaming.
        
        Args:
            existing_cases: Existing test cases
            requirement: Requirement description
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            New supplemented test cases
        """
        # Build prompt
        prompt = self.build_supplement_prompt(
            existing_cases=existing_cases,
            requirement=requirement
        )
        
        system_message = "你是一个专业的测试用例补充专家,擅长识别测试覆盖的缺失并补充新用例。"
        
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
