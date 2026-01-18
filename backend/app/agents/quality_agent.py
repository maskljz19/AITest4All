"""Quality Analysis Agent"""

import json
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

from app.agents.base_agent import BaseAgent, ModelProvider


class QualityAgent(BaseAgent):
    """
    Agent for analyzing test case quality and providing improvement suggestions.
    
    Analyzes:
    - Requirement coverage
    - Duplicate cases
    - SMART principle compliance
    - Missing scenarios
    - Quality scoring
    """
    
    def __init__(
        self,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 3000
    ):
        """
        Initialize quality analysis agent.
        
        Args:
            model_provider: LLM provider
            model_name: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(
            agent_type="quality",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def build_prompt(
        self,
        requirement_analysis: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]],
        defect_history: Optional[str] = None
    ) -> str:
        """
        Build prompt for quality analysis.
        
        Args:
            requirement_analysis: Requirement analysis result
            scenarios: List of test scenarios
            test_cases: List of test cases
            defect_history: Historical defect information
            
        Returns:
            Formatted prompt
        """
        prompt = f"""你是一个专业的测试质量分析专家。请分析测试用例的质量,并提供改进建议。

需求分析:
功能点: {json.dumps(requirement_analysis.get('function_points', []), ensure_ascii=False)}
业务规则: {json.dumps(requirement_analysis.get('business_rules', []), ensure_ascii=False)}
测试重点: {json.dumps(requirement_analysis.get('test_focus', []), ensure_ascii=False)}
风险点: {json.dumps(requirement_analysis.get('risk_points', []), ensure_ascii=False)}

测试场景数量: {len(scenarios)}
测试用例数量: {len(test_cases)}

测试场景:
{json.dumps(scenarios, ensure_ascii=False, indent=2)}

测试用例:
{json.dumps(test_cases, ensure_ascii=False, indent=2)}
"""
        
        if defect_history:
            prompt += f"""

历史缺陷参考:
{defect_history}
"""
        
        prompt += """

请从以下维度分析测试质量:

1. 覆盖度分析:
   - 计算需求覆盖率(已覆盖的功能点/总功能点)
   - 列出未覆盖的功能点
   - 列出缺失的测试场景

2. 用例质量分析:
   - 识别重复或冗余的用例
   - 识别不符合SMART原则的用例:
     * Specific(具体的): 步骤是否具体明确
     * Measurable(可衡量的): 结果是否可验证
     * Achievable(可实现的): 步骤是否可执行
     * Relevant(相关的): 是否与需求相关
     * Time-bound(有时限的): 是否有明确顺序
   - 识别测试数据不完整的用例

3. 场景完整性分析:
   - 对比历史缺陷,列出缺失的重要场景
   - 识别风险点是否有对应的测试场景

4. 改进建议:
   - 针对发现的问题提供具体的改进建议
   - 建议补充的测试场景
   - 建议优化的测试用例

5. 质量评分:
   - 覆盖度评分(0-100)
   - 用例质量评分(0-100)
   - 总体质量评分(0-100)

请按照以下JSON格式输出分析结果:
{
  "coverage_analysis": {
    "coverage_rate": 85,
    "uncovered_points": ["未覆盖的功能点"],
    "missing_scenarios": ["缺失的场景"]
  },
  "quality_analysis": {
    "duplicate_cases": ["TC001与TC005重复"],
    "non_smart_cases": [
      {
        "case_id": "TC003",
        "issues": ["步骤不够具体", "缺少预期结果"]
      }
    ],
    "incomplete_data": ["TC007缺少测试数据"]
  },
  "suggestions": [
    "建议补充并发登录的测试场景",
    "TC003需要细化操作步骤",
    "建议补充历史缺陷中的密码重置问题测试"
  ],
  "quality_score": {
    "coverage_score": 85,
    "quality_score": 78,
    "total_score": 81
  }
}

要求:
1. 分析要全面深入
2. 问题要具体明确
3. 建议要可操作
4. 评分要客观合理
5. 输出必须是有效的JSON格式

请直接输出JSON,不要添加任何其他说明文字。
"""
        
        return prompt
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into quality analysis result.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed quality analysis dict
            
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
            
            # Ensure required structure
            if "coverage_analysis" not in result:
                result["coverage_analysis"] = {}
            if "quality_analysis" not in result:
                result["quality_analysis"] = {}
            if "suggestions" not in result:
                result["suggestions"] = []
            if "quality_score" not in result:
                result["quality_score"] = {}
            
            # Remove scenario_completeness if present (not in response model)
            if "scenario_completeness" in result:
                # Merge scenario_completeness suggestions into main suggestions
                sc = result.pop("scenario_completeness")
                if "missing_risk_scenarios" in sc:
                    for scenario in sc["missing_risk_scenarios"]:
                        result["suggestions"].append(f"建议补充场景: {scenario}")
                if "defect_related_gaps" in sc:
                    for gap in sc["defect_related_gaps"]:
                        result["suggestions"].append(f"历史缺陷相关: {gap}")
            
            # Ensure coverage_analysis fields
            coverage = result["coverage_analysis"]
            if "coverage_rate" not in coverage:
                coverage["coverage_rate"] = 0
            # Remove covered_points if present (not in response model)
            if "covered_points" in coverage:
                coverage.pop("covered_points")
            if "uncovered_points" not in coverage:
                coverage["uncovered_points"] = []
            if "missing_scenarios" not in coverage:
                coverage["missing_scenarios"] = []
            
            # Ensure quality_analysis fields
            quality = result["quality_analysis"]
            if "duplicate_cases" not in quality:
                quality["duplicate_cases"] = []
            if "non_smart_cases" not in quality:
                quality["non_smart_cases"] = []
            if "incomplete_data" not in quality:
                quality["incomplete_data"] = []
            
            # Ensure quality_score fields
            score = result["quality_score"]
            if "coverage_score" not in score:
                score["coverage_score"] = 0
            if "quality_score" not in score:
                score["quality_score"] = 0
            if "total_score" not in score:
                score["total_score"] = 0
            
            return result
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")
    
    async def analyze_quality(
        self,
        requirement_analysis: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]],
        defect_kb_ids: Optional[List[int]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze test case quality.
        
        Args:
            requirement_analysis: Requirement analysis result
            scenarios: List of test scenarios
            test_cases: List of test cases
            defect_kb_ids: IDs of defect knowledge bases
            stream: Whether to stream response
            
        Returns:
            Quality analysis result
        """
        # TODO: Retrieve defect history from knowledge base if needed
        defect_history = None
        
        system_message = "你是一个专业的测试质量分析专家,擅长评估测试用例的完整性和有效性。"
        
        return await self.generate(
            stream=stream,
            system_message=system_message,
            requirement_analysis=requirement_analysis,
            scenarios=scenarios,
            test_cases=test_cases,
            defect_history=defect_history
        )
    
    def calculate_coverage(
        self,
        requirement_analysis: Dict[str, Any],
        test_cases: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate requirement coverage rate.
        
        Args:
            requirement_analysis: Requirement analysis result
            test_cases: List of test cases
            
        Returns:
            Coverage rate (0-100)
        """
        function_points = requirement_analysis.get("function_points", [])
        if not function_points:
            return 0.0
        
        # Extract covered points from test case titles and descriptions
        covered_points = set()
        
        for case in test_cases:
            title = case.get("title", "").lower()
            for point in function_points:
                if point.lower() in title:
                    covered_points.add(point)
        
        coverage_rate = (len(covered_points) / len(function_points)) * 100
        return round(coverage_rate, 2)
    
    def identify_duplicates(self, test_cases: List[Dict[str, Any]]) -> List[str]:
        """
        Identify duplicate or redundant test cases.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of duplicate descriptions
        """
        duplicates = []
        seen_titles = defaultdict(list)
        
        # Group by similar titles
        for case in test_cases:
            title = case.get("title", "").lower().strip()
            case_id = case.get("case_id", "")
            seen_titles[title].append(case_id)
        
        # Find duplicates
        for title, case_ids in seen_titles.items():
            if len(case_ids) > 1:
                duplicates.append(f"{' 与 '.join(case_ids)} 标题相似或重复")
        
        return duplicates
    
    def check_smart_compliance(self, test_case: Dict[str, Any]) -> List[str]:
        """
        Check if test case complies with SMART principle.
        
        Args:
            test_case: Test case to check
            
        Returns:
            List of non-compliance issues
        """
        issues = []
        
        # Specific: steps should be detailed
        steps = test_case.get("steps", [])
        if not steps:
            issues.append("缺少测试步骤")
        else:
            for step in steps:
                if not step.get("action") or len(step.get("action", "")) < 5:
                    issues.append(f"步骤{step.get('step_no')}不够具体")
        
        # Measurable: should have expected results
        if not test_case.get("expected_result"):
            issues.append("缺少预期结果")
        
        # Achievable: avoid vague terms
        vague_terms = ["适当", "合理", "正常", "正确", "合适"]
        for step in steps:
            action = step.get("action", "")
            for term in vague_terms:
                if term in action:
                    issues.append(f"步骤{step.get('step_no')}包含模糊表述: {term}")
                    break
        
        # Relevant: should have title and priority
        if not test_case.get("title"):
            issues.append("缺少标题")
        if not test_case.get("priority"):
            issues.append("缺少优先级")
        
        # Time-bound: steps should be ordered
        if steps:
            step_numbers = [step.get("step_no", 0) for step in steps]
            if step_numbers != sorted(step_numbers):
                issues.append("步骤顺序不正确")
        
        return issues
    
    def calculate_quality_score(
        self,
        requirement_analysis: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate quality scores.
        
        Args:
            requirement_analysis: Requirement analysis result
            scenarios: List of test scenarios
            test_cases: List of test cases
            
        Returns:
            Dict with coverage_score, quality_score, and total_score
        """
        # Coverage score
        coverage_score = self.calculate_coverage(requirement_analysis, test_cases)
        
        # Quality score based on SMART compliance
        total_cases = len(test_cases)
        if total_cases == 0:
            quality_score = 0.0
        else:
            compliant_cases = 0
            for case in test_cases:
                issues = self.check_smart_compliance(case)
                if not issues:
                    compliant_cases += 1
            quality_score = (compliant_cases / total_cases) * 100
        
        # Total score (weighted average)
        total_score = (coverage_score * 0.6 + quality_score * 0.4)
        
        return {
            "coverage_score": round(coverage_score, 2),
            "quality_score": round(quality_score, 2),
            "total_score": round(total_score, 2)
        }


    async def analyze(
        self,
        requirement_analysis: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]],
        defect_history: Optional[str] = None,
        stream_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze test case quality with optional streaming.
        
        Args:
            requirement_analysis: Requirement analysis result
            scenarios: List of test scenarios
            test_cases: List of test cases
            defect_history: Defect history context string
            stream_callback: Optional callback for streaming chunks
            
        Returns:
            Quality analysis result
        """
        # Build prompt
        prompt = self.build_prompt(
            requirement_analysis=requirement_analysis,
            scenarios=scenarios,
            test_cases=test_cases,
            defect_history=defect_history
        )
        
        system_message = "你是一个专业的测试质量分析专家,擅长评估测试用例的质量和完整性。"
        
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
