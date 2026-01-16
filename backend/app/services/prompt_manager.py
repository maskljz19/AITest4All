"""Agent Prompt Management Service"""

import os
from pathlib import Path
from typing import Dict, Optional
from app.core.config import settings


class PromptManager:
    """
    Manages agent system prompts from configuration files.
    
    Prompts are stored in the agent_prompts directory with the following structure:
    - requirement_agent.txt
    - scenario_agent.txt
    - case_agent.txt
    - code_agent.txt
    - quality_agent.txt
    - optimize_agent.txt
    """
    
    def __init__(self):
        """Initialize prompt manager"""
        self.prompts_dir = Path(settings.agent_prompts_dir)
        self._cache: Dict[str, str] = {}
        self._ensure_prompts_dir()
        self._load_default_prompts()
    
    def _ensure_prompts_dir(self):
        """Ensure prompts directory exists"""
        if not self.prompts_dir.exists():
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_default_prompts(self):
        """Load default prompts if files don't exist"""
        default_prompts = {
            "requirement_agent": """你是一个专业的需求分析专家。你的任务是分析用户提供的需求文档，提取关键信息并生成结构化的需求分析报告。

请按照以下格式输出：
1. 功能概述：简要描述主要功能
2. 核心需求：列出关键需求点
3. 技术要点：识别技术实现要点
4. 边界条件：识别边界情况和异常场景
5. 测试重点：建议测试关注点

请确保输出清晰、结构化，便于后续测试用例生成。""",
            
            "scenario_agent": """你是一个测试场景设计专家。基于需求分析结果，你需要设计全面的测试场景。

请按照以下维度设计测试场景：
1. 正常场景：常规业务流程
2. 边界场景：边界值、临界条件
3. 异常场景：错误处理、异常情况
4. 性能场景：高负载、并发情况
5. 安全场景：权限、数据安全

每个场景应包含：
- 场景名称
- 场景描述
- 前置条件
- 预期结果""",
            
            "case_agent": """你是一个测试用例编写专家。基于测试场景，你需要生成详细的测试用例。

测试用例格式：
- 用例ID：唯一标识
- 用例标题：简洁描述
- 优先级：P0/P1/P2/P3
- 前置条件：执行前需满足的条件
- 测试步骤：详细的操作步骤
- 预期结果：每步的预期输出
- 测试数据：所需的测试数据

请确保用例：
1. 步骤清晰，可执行
2. 预期结果明确
3. 覆盖场景要求
4. 包含必要的测试数据""",
            
            "code_agent": """你是一个自动化测试代码专家。你需要将测试用例转换为可执行的自动化测试代码。

请根据以下要求生成代码：
1. 使用pytest框架
2. 遵循PEP 8代码规范
3. 包含必要的注释
4. 使用合适的断言
5. 处理异常情况
6. 包含测试数据准备和清理

代码结构：
- 导入必要的库
- 定义测试类/函数
- 实现测试步骤
- 添加断言验证
- 清理测试数据""",
            
            "quality_agent": """你是一个测试质量评审专家。你需要评估测试用例的质量并提供改进建议。

评审维度：
1. 完整性：是否覆盖所有场景
2. 准确性：步骤和预期结果是否准确
3. 可执行性：是否可以实际执行
4. 可维护性：是否易于理解和维护
5. 有效性：是否能发现缺陷

输出格式：
- 质量评分：0-100分
- 优点：列出做得好的地方
- 问题：列出存在的问题
- 建议：提供具体改进建议""",
            
            "optimize_agent": """你是一个测试优化专家。你需要优化测试用例，提高测试效率和质量。

优化方向：
1. 去重：合并重复的测试用例
2. 精简：删除冗余的测试步骤
3. 增强：补充遗漏的测试场景
4. 重组：优化测试用例结构
5. 数据：优化测试数据设计

输出：
- 优化后的测试用例
- 优化说明：解释优化的原因和效果
- 覆盖率提升：说明覆盖率的改进"""
        }
        
        for agent_type, default_prompt in default_prompts.items():
            prompt_file = self.prompts_dir / f"{agent_type}.txt"
            if not prompt_file.exists():
                prompt_file.write_text(default_prompt, encoding="utf-8")
    
    def get_prompt(self, agent_type: str) -> Optional[str]:
        """
        Get prompt for specified agent type.
        
        Args:
            agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
            
        Returns:
            Prompt text or None if not found
        """
        # Check cache first
        if agent_type in self._cache:
            return self._cache[agent_type]
        
        # Load from file
        prompt_file = self.prompts_dir / f"{agent_type}.txt"
        if prompt_file.exists():
            prompt = prompt_file.read_text(encoding="utf-8")
            self._cache[agent_type] = prompt
            return prompt
        
        return None
    
    def set_prompt(self, agent_type: str, prompt: str) -> bool:
        """
        Set prompt for specified agent type.
        
        Args:
            agent_type: Agent type
            prompt: Prompt text
            
        Returns:
            True if successful
        """
        try:
            prompt_file = self.prompts_dir / f"{agent_type}.txt"
            prompt_file.write_text(prompt, encoding="utf-8")
            self._cache[agent_type] = prompt
            return True
        except Exception:
            return False
    
    def list_prompts(self) -> Dict[str, str]:
        """
        List all available prompts.
        
        Returns:
            Dict mapping agent type to prompt text
        """
        prompts = {}
        for prompt_file in self.prompts_dir.glob("*.txt"):
            agent_type = prompt_file.stem
            prompts[agent_type] = self.get_prompt(agent_type)
        return prompts
    
    def reload_prompts(self):
        """Reload all prompts from disk"""
        self._cache.clear()


# Global prompt manager instance
prompt_manager = PromptManager()
