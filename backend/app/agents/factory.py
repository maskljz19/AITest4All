"""Agent Factory - Create agents with configuration"""

from typing import Optional
from sqlalchemy import select
from app.agents.base_agent import BaseAgent, ModelProvider
from app.agents.requirement_agent import RequirementAgent
from app.agents.scenario_agent import ScenarioAgent
from app.agents.case_agent import CaseAgent
from app.agents.code_agent import CodeAgent
from app.agents.quality_agent import QualityAgent
from app.agents.optimize_agent import OptimizeAgent
from app.core.config import settings
from app.models.agent_config import AgentConfig
from app.core.database import get_async_session
import asyncio


async def get_agent_config_from_db(agent_type: str) -> Optional[AgentConfig]:
    """
    Get agent configuration from database.
    
    Args:
        agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
        
    Returns:
        AgentConfig instance or None if not found
    """
    try:
        async with get_async_session() as db:
            stmt = select(AgentConfig).where(AgentConfig.agent_type == agent_type)
            result = await db.execute(stmt)
            config = result.scalar_one_or_none()
            return config
    except Exception as e:
        import logging
        logging.warning(f"Failed to load agent config from database: {e}")
        return None


def get_model_config_for_agent(agent_type: str) -> tuple[str, str, dict, str]:
    """
    Get model configuration for specific agent type from database or settings.
    
    Args:
        agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
        
    Returns:
        Tuple of (provider, model_name, model_params, prompt_template)
    """
    # Try to load from database first
    try:
        config = asyncio.run(get_agent_config_from_db(agent_type))
        if config:
            model_params = config.model_params or {}
            return (
                config.model_provider,
                config.model_name,
                model_params,
                config.prompt_template
            )
    except Exception as e:
        import logging
        logging.warning(f"Failed to load config from database, using settings: {e}")
    
    # Fallback to settings
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
    model_params = {
        "temperature": settings.default_temperature,
        "max_tokens": settings.default_max_tokens
    }
    
    return provider, model_name, model_params, ""


def create_agent(
    agent_type: str,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> BaseAgent:
    """
    Create agent instance with configuration from database or settings.
    
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
    # Get configuration from database or settings
    default_provider, default_model, default_params, prompt_template = get_model_config_for_agent(agent_type)
    
    # Use provided values or defaults
    provider = model_provider or default_provider
    model = model_name or default_model
    temp = temperature if temperature is not None else default_params.get("temperature", settings.default_temperature)
    tokens = max_tokens if max_tokens is not None else default_params.get("max_tokens", settings.default_max_tokens)
    
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
    
    # Create agent instance
    agent = agent_class(
        model_provider=provider_enum,
        model_name=model,
        temperature=temp,
        max_tokens=tokens
    )
    
    # Override system prompt if loaded from database
    if prompt_template:
        agent.system_prompt = prompt_template
    
    return agent


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
