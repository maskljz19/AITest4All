"""Test Case Generation Agent"""

import json
import re
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent, ModelProvider
from app.services.script_executor import ScriptExecutor


class CaseAgent(BaseAgent):
    """
    Agent for generating detailed test cases from scenarios.
    
    Generates test cases with:
    - Test steps
    - Test data (with script integration)
    - Expected results
    - Pre/post conditions
    """
    
    def __init__(
        self,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 3000,
        script_executor: Optional[ScriptExecutor] = None
    ):
        """
        Initialize test case generation agent.
        
        Args:
            model_provider: LLM provider
            model_name: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            script_executor: Script executor for generating test data
        """
        super().__init__(
            agent_type="case",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.script_executor = script_executor
    
    def build_prompt(
        self,
        scenario: Dict[str, Any],
        template: Optional[Dict[str, Any]] = None,
        available_scripts: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build prompt for test case generation.
        
        Args:
            scenario: Test scenario
            template: Optional case template
            available_scripts: List of available scripts for data generation
            
        Returns:
            Formatted prompt
        """
        prompt = f"""你是一个专业的测试用例编写专家。请根据测试场景生成详细的测试用例。

测试场景:
- 场景ID: {scenario.get('scenario_id', '')}
- 场景名称: {scenario.get('name', '')}
- 场景描述: {scenario.get('description', '')}
- 前置条件: {scenario.get('precondition', '')}
- 预期结果: {scenario.get('expected_result', '')}
- 优先级: {scenario.get('priority', 'P1')}
- 分类: {scenario.get('category', 'normal')}
"""
        
        # Add template guidance if provided
        if template:
            prompt += f"""

用例模板:
{json.dumps(template, ensure_ascii=False, indent=2)}

请按照模板格式生成用例。
"""
        
        # Add available scripts information
        if available_scripts:
            script_info = "\n".join([
                f"- {script['name']}: {script.get('description', '')}"
                for script in available_scripts
            ])
            prompt += f"""

可用的数据生成脚本:
{script_info}

如果需要生成测试数据,可以在test_data字段中使用占位符,格式为: {{{{script:脚本名称}}}}
例如: {{"phone": "{{{{script:generate_phone_number}}}}"}}
"""
        
        prompt += """

请按照以下JSON格式输出测试用例:
{
  "case_id": "TC001",
  "title": "用例标题",
  "test_type": "ui/api/unit",
  "priority": "P0/P1/P2",
  "precondition": "前置条件描述",
  "steps": [
    {
      "step_no": 1,
      "action": "操作描述",
      "data": "测试数据",
      "expected": "预期结果"
    }
  ],
  "test_data": {
    "field1": "value1",
    "field2": "value2"
  },
  "expected_result": "整体预期结果",
  "postcondition": "后置条件(清理操作)"
}

要求:
1. 用例标题要简洁明确
2. 测试步骤要详细具体,每一步都要清晰
3. 测试数据要真实有效,符合实际场景
4. 预期结果要明确可验证
5. 遵循SMART原则:
   - Specific(具体的): 步骤和结果要具体明确
   - Measurable(可衡量的): 结果要可验证
   - Achievable(可实现的): 步骤要可执行
   - Relevant(相关的): 与场景相关
   - Time-bound(有时限的): 明确操作顺序
6. 输出必须是有效的JSON格式

请直接输出JSON,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into test case.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed test case dict
            
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
            test_case = json.loads(response)
            
            # Ensure required fields
            if "case_id" not in test_case:
                test_case["case_id"] = "TC001"
            if "title" not in test_case:
                test_case["title"] = "测试用例"
            if "test_type" not in test_case:
                test_case["test_type"] = "ui"
            if "priority" not in test_case:
                test_case["priority"] = "P1"
            if "precondition" not in test_case:
                test_case["precondition"] = ""
            if "steps" not in test_case:
                test_case["steps"] = []
            if "test_data" not in test_case:
                test_case["test_data"] = {}
            if "expected_result" not in test_case:
                test_case["expected_result"] = ""
            if "postcondition" not in test_case:
                test_case["postcondition"] = ""
            
            # Validate steps structure
            for i, step in enumerate(test_case["steps"]):
                if "step_no" not in step:
                    step["step_no"] = i + 1
                if "action" not in step:
                    step["action"] = ""
                if "data" not in step:
                    step["data"] = ""
                if "expected" not in step:
                    step["expected"] = ""
            
            return test_case
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")
    
    async def generate_case(
        self,
        scenario: Dict[str, Any],
        template_id: Optional[int] = None,
        script_ids: Optional[List[int]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate test case for a scenario.
        
        Args:
            scenario: Test scenario
            template_id: Optional template ID
            script_ids: Optional script IDs for data generation
            stream: Whether to stream response
            
        Returns:
            Generated test case
        """
        # TODO: Load template from database if template_id provided
        template = None
        
        # TODO: Load available scripts from database if script_ids provided
        available_scripts = None
        
        system_message = "你是一个专业的测试用例编写专家,擅长编写详细、可执行的测试用例。"
        
        test_case = await self.generate(
            stream=stream,
            system_message=system_message,
            scenario=scenario,
            template=template,
            available_scripts=available_scripts
        )
        
        # Process script placeholders in test data
        if self.script_executor and isinstance(test_case, dict):
            test_case = await self._process_script_placeholders(test_case)
        
        return test_case
    
    async def _process_script_placeholders(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process script placeholders in test data.
        
        Args:
            test_case: Test case with potential script placeholders
            
        Returns:
            Test case with executed script results
        """
        test_data = test_case.get("test_data", {})
        
        # Pattern to match {{script:script_name}}
        script_pattern = re.compile(r'\{\{script:([^}]+)\}\}')
        
        for key, value in test_data.items():
            if isinstance(value, str):
                match = script_pattern.search(value)
                if match:
                    script_name = match.group(1).strip()
                    try:
                        # Execute script to generate data
                        result = await self.script_executor.execute_by_name(script_name)
                        if result.get("success"):
                            test_data[key] = result.get("output", "")
                    except Exception as e:
                        # Keep placeholder if script execution fails
                        print(f"Script execution failed for {script_name}: {e}")
        
        test_case["test_data"] = test_data
        return test_case
    
    def validate_smart_principle(self, test_case: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate test case against SMART principle.
        
        Args:
            test_case: Test case to validate
            
        Returns:
            Dict with validation issues for each SMART criterion
        """
        issues = {
            "specific": [],
            "measurable": [],
            "achievable": [],
            "relevant": [],
            "time_bound": []
        }
        
        # Check Specific: steps should be detailed
        steps = test_case.get("steps", [])
        if not steps:
            issues["specific"].append("测试用例缺少测试步骤")
        else:
            for step in steps:
                if not step.get("action") or len(step.get("action", "")) < 5:
                    issues["specific"].append(f"步骤{step.get('step_no')}的操作描述不够具体")
        
        # Check Measurable: expected results should be clear
        if not test_case.get("expected_result"):
            issues["measurable"].append("缺少整体预期结果")
        
        for step in steps:
            if not step.get("expected"):
                issues["measurable"].append(f"步骤{step.get('step_no')}缺少预期结果")
        
        # Check Achievable: steps should be executable
        vague_terms = ["适当", "合理", "正常", "正确"]
        for step in steps:
            action = step.get("action", "")
            if any(term in action for term in vague_terms):
                issues["achievable"].append(f"步骤{step.get('step_no')}包含模糊表述")
        
        # Check Relevant: should have title and priority
        if not test_case.get("title"):
            issues["relevant"].append("缺少用例标题")
        if not test_case.get("priority"):
            issues["relevant"].append("缺少优先级")
        
        # Check Time-bound: steps should be ordered
        if steps:
            step_numbers = [step.get("step_no", 0) for step in steps]
            if step_numbers != sorted(step_numbers):
                issues["time_bound"].append("测试步骤顺序不正确")
        
        # Remove empty issue lists
        issues = {k: v for k, v in issues.items() if v}
        
        return issues
    
    async def generate_cases_batch(
        self,
        scenarios: List[Dict[str, Any]],
        template_id: Optional[int] = None,
        script_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases for multiple scenarios.
        
        Args:
            scenarios: List of test scenarios
            template_id: Optional template ID
            script_ids: Optional script IDs
            
        Returns:
            List of generated test cases
        """
        test_cases = []
        
        for i, scenario in enumerate(scenarios):
            try:
                test_case = await self.generate_case(
                    scenario=scenario,
                    template_id=template_id,
                    script_ids=script_ids,
                    stream=False
                )
                
                # Assign unique case ID
                test_case["case_id"] = f"TC{i+1:03d}"
                
                test_cases.append(test_case)
            
            except Exception as e:
                print(f"Failed to generate case for scenario {scenario.get('scenario_id')}: {e}")
                continue
        
        return test_cases


    async def generate(
        self,
        scenarios: List[Dict[str, Any]],
        template_id: Optional[int] = None,
        script_ids: Optional[List[int]] = None,
        stream_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases for scenarios with optional streaming.
        
        Args:
            scenarios: List of test scenarios
            template_id: Optional template ID
            script_ids: Optional script IDs
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            List of generated test cases
        """
        test_cases = []
        
        for i, scenario in enumerate(scenarios):
            try:
                # Build prompt for this scenario
                prompt = self.build_prompt(
                    scenario=scenario,
                    template=None,  # TODO: Load template if template_id provided
                    available_scripts=[]  # TODO: Load scripts if script_ids provided
                )
                
                system_message = "你是一个专业的测试用例设计专家,擅长编写详细的测试用例。"
                
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
                    
                    test_case = self.parse_response(response_text)
                else:
                    # Non-streaming response
                    response = await self._call_llm_with_retry(
                        prompt=prompt,
                        system_message=system_message,
                        stream=False
                    )
                    test_case = self.parse_response(response)
                
                # Assign unique case ID
                test_case["case_id"] = f"TC{i+1:03d}"
                test_cases.append(test_case)
            
            except Exception as e:
                print(f"Failed to generate case for scenario {scenario.get('scenario_id')}: {e}")
                continue
        
        return test_cases
