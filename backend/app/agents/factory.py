"""Agent Factory - Create agents with configuration"""

from typing import Optional
from app.agents.base_agent import BaseAgent, ModelProvider
from app.agents.requirement_agent import RequirementAgent
from app.agents.scenario_agent import ScenarioAgent
from app.agents.case_agent import CaseAgent
from app.agents.code_agent import CodeAgent
from app.agents.quality_agent import QualityAgent
from app.agents.optimize_agent import OptimizeAgent
from app.core.config import settings


def get_model_config_for_agent(agent_type: str) -> tuple[str, str]:
    """
    Get model configuration for specific agent type.
    
    Args:
        agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
        
    Returns:
        Tuple of (provider, model_name)
    """
    agent_model_map = {
        "requirement": settings.requirement_agent_model,
        "scenario": settings.scenario_agent_model,
        "case": settings.case_agent_model,
        "code": settings.code_agent_model,
        "quality": settings.quality_agent_model,
        "optimize": settings.optimize_agent_model
    }
    
    model_name = agent_model_map.get(agent_type) or settings.default_model_name
    provider = settings.default_model_provider
    
    return provider, model_name


def create_agent(
    agent_type: str,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> BaseAgent:
    """
    Create agent instance with configuration.
    
    Args:
        agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
        model_provider: Optional model provider override
        model_name: Optional model name override
        temperature: Optional temperature override
        max_tokens: Optional max tokens override
        
    Returns:
        Agent instance
        
    Raises:
        ValueError: If agent type is invalid
    """
    # Get default configuration
    default_provider, default_model = get_model_config_for_agent(agent_type)
    
    # Use provided values or defaults
    provider = model_provider or default_provider
    model = model_name or default_model
    temp = temperature if temperature is not None else settings.default_temperature
    tokens = max_tokens if max_tokens is not None else settings.default_max_tokens
    
    # Convert provider string to enum
    provider_enum = ModelProvider(provider)
    
    # Create agent based on type
    agent_classes = {
        "requirement": RequirementAgent,
        "scenario": ScenarioAgent,
        "case": CaseAgent,
        "code": CodeAgent,
        "quality": QualityAgent,
        "optimize": OptimizeAgent
    }
    
    agent_class = agent_classes.get(agent_type)
    if not agent_class:
        raise ValueError(f"Invalid agent type: {agent_type}")
    
    return agent_class(
        model_provider=provider_enum,
        model_name=model,
        temperature=temp,
        max_tokens=tokens
    )


def create_requirement_agent(**kwargs) -> RequirementAgent:
    """Create requirement agent with configuration"""
    return create_agent("requirement", **kwargs)


def create_scenario_agent(**kwargs) -> ScenarioAgent:
    """Create scenario agent with configuration"""
    return create_agent("scenario", **kwargs)


def create_case_agent(**kwargs) -> CaseAgent:
    """Create case agent with configuration"""
    return create_agent("case", **kwargs)


def create_code_agent(**kwargs) -> CodeAgent:
    """Create code agent with configuration"""
    return create_agent("code", **kwargs)


def create_quality_agent(**kwargs) -> QualityAgent:
    """Create quality agent with configuration"""
    return create_agent("quality", **kwargs)


def create_optimize_agent(**kwargs) -> OptimizeAgent:
    """Create optimize agent with configuration"""
    return create_agent("optimize", **kwargs)
