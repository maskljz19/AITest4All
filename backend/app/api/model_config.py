"""Model Configuration Management API"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings


router = APIRouter(prefix="/model-config", tags=["model-config"])


class ModelConfig(BaseModel):
    """Model configuration"""
    provider: str = Field(description="Model provider (openai/anthropic/local)")
    model_name: str = Field(description="Model name")
    temperature: float = Field(ge=0, le=2, description="Temperature (0-2)")
    max_tokens: int = Field(gt=0, description="Maximum tokens")
    
    model_config = {"protected_namespaces": ()}


class ModelConfigResponse(BaseModel):
    """Model configuration response"""
    default: ModelConfig
    openai_api_base: str
    anthropic_api_base: str
    agent_specific: dict


class AgentModelConfig(BaseModel):
    """Agent-specific model configuration"""
    requirement_agent: Optional[str] = None
    scenario_agent: Optional[str] = None
    case_agent: Optional[str] = None
    code_agent: Optional[str] = None
    quality_agent: Optional[str] = None
    optimize_agent: Optional[str] = None


@router.get("/", response_model=ModelConfigResponse)
async def get_model_config():
    """
    Get current model configuration.
    
    Returns:
        Model configuration including default and agent-specific settings
    """
    return {
        "default": {
            "provider": settings.default_model_provider,
            "model_name": settings.default_model_name,
            "temperature": settings.default_temperature,
            "max_tokens": settings.default_max_tokens
        },
        "openai_api_base": settings.openai_api_base,
        "anthropic_api_base": settings.anthropic_api_base,
        "agent_specific": {
            "requirement_agent": settings.requirement_agent_model or settings.default_model_name,
            "scenario_agent": settings.scenario_agent_model or settings.default_model_name,
            "case_agent": settings.case_agent_model or settings.default_model_name,
            "code_agent": settings.code_agent_model or settings.default_model_name,
            "quality_agent": settings.quality_agent_model or settings.default_model_name,
            "optimize_agent": settings.optimize_agent_model or settings.default_model_name
        }
    }


@router.get("/providers")
async def get_available_providers():
    """
    Get available model providers and their status.
    
    Returns:
        List of providers with configuration status
    """
    providers = []
    
    # OpenAI
    providers.append({
        "name": "openai",
        "configured": bool(settings.openai_api_key),
        "api_base": settings.openai_api_base,
        "models": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    })
    
    # Anthropic
    providers.append({
        "name": "anthropic",
        "configured": bool(settings.anthropic_api_key),
        "api_base": settings.anthropic_api_base,
        "models": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]
    })
    
    # Local (not yet implemented)
    providers.append({
        "name": "local",
        "configured": False,
        "api_base": "N/A",
        "models": []
    })
    
    return {"providers": providers}


@router.get("/agent/{agent_type}")
async def get_agent_model_config(agent_type: str):
    """
    Get model configuration for specific agent.
    
    Args:
        agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
        
    Returns:
        Model configuration for the agent
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
    
    return {
        "agent_type": agent_type,
        "model_name": model_name,
        "provider": settings.default_model_provider,
        "temperature": settings.default_temperature,
        "max_tokens": settings.default_max_tokens,
        "using_default": not bool(agent_model_map.get(agent_type))
    }
