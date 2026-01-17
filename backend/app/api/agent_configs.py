"""Agent Configuration Management API"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.agent_config import AgentConfig
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/agent-configs", tags=["agent-configs"])


# Request/Response Models
class AgentConfigUpdateRequest(BaseModel):
    """Request model for updating agent configuration"""
    agent_name: Optional[str] = None
    model_provider: Optional[str] = None  # openai/anthropic/local
    model_name: Optional[str] = None
    prompt_template: Optional[str] = None
    model_params: Optional[dict] = None  # {"temperature": 0.7, "max_tokens": 2000}
    knowledge_bases: Optional[List[int]] = None
    scripts: Optional[List[int]] = None


class AgentConfigResponse(BaseModel):
    """Response model for agent configuration"""
    id: int
    agent_type: str
    agent_name: str
    model_provider: str
    model_name: str
    prompt_template: str
    model_params: dict
    knowledge_bases: List[int]
    scripts: List[int]
    is_default: bool
    created_at: datetime
    updated_at: datetime


@router.get("")
async def list_agent_configs(
    db: AsyncSession = Depends(get_db)
):
    """
    List all agent configurations
    
    Returns configurations for all agent types
    """
    try:
        stmt = select(AgentConfig).order_by(AgentConfig.agent_type)
        result = await db.execute(stmt)
        configs = result.scalars().all()
        
        # Format response
        data = []
        for config in configs:
            data.append({
                "id": config.id,
                "agent_type": config.agent_type,
                "agent_name": config.agent_name,
                "model_provider": config.model_provider,
                "model_name": config.model_name,
                "prompt_template": config.prompt_template,
                "model_params": config.model_params,
                "knowledge_bases": config.knowledge_bases or [],
                "scripts": config.scripts or [],
                "is_default": config.is_default,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agent configs: {str(e)}"
        )


@router.get("/{agent_type}")
async def get_agent_config(
    agent_type: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent configuration by type
    
    Valid agent types: requirement/scenario/case/code/quality
    """
    try:
        # Validate agent type
        valid_types = ['requirement', 'scenario', 'case', 'code', 'quality']
        if agent_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type. Must be one of: {', '.join(valid_types)}"
            )
        
        stmt = select(AgentConfig).where(AgentConfig.agent_type == agent_type)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration for agent type '{agent_type}' not found"
            )
        
        return {
            "success": True,
            "data": {
                "id": config.id,
                "agent_type": config.agent_type,
                "agent_name": config.agent_name,
                "model_provider": config.model_provider,
                "model_name": config.model_name,
                "prompt_template": config.prompt_template,
                "model_params": config.model_params,
                "knowledge_bases": config.knowledge_bases or [],
                "scripts": config.scripts or [],
                "is_default": config.is_default,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent config: {str(e)}"
        )


@router.put("/{agent_type}")
async def update_agent_config(
    agent_type: str,
    request: AgentConfigUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update agent configuration
    
    Updates the configuration for the specified agent type
    """
    try:
        # Validate agent type
        valid_types = ['requirement', 'scenario', 'case', 'code', 'quality']
        if agent_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type. Must be one of: {', '.join(valid_types)}"
            )
        
        stmt = select(AgentConfig).where(AgentConfig.agent_type == agent_type)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration for agent type '{agent_type}' not found"
            )
        
        # Update fields
        if request.agent_name is not None:
            config.agent_name = request.agent_name
        
        if request.model_provider is not None:
            # Validate model provider
            valid_providers = ['openai', 'anthropic', 'local', 'other']
            if request.model_provider not in valid_providers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model provider. Must be one of: {', '.join(valid_providers)}"
                )
            config.model_provider = request.model_provider
        
        if request.model_name is not None:
            config.model_name = request.model_name
        
        if request.prompt_template is not None:
            config.prompt_template = request.prompt_template
        
        if request.model_params is not None:
            config.model_params = request.model_params
        
        if request.knowledge_bases is not None:
            config.knowledge_bases = request.knowledge_bases
        
        if request.scripts is not None:
            config.scripts = request.scripts
        
        config.updated_at = datetime.utcnow()
        config.is_default = False  # Mark as customized
        
        await db.commit()
        await db.refresh(config)
        
        return {
            "success": True,
            "message": f"Agent configuration for '{agent_type}' updated successfully",
            "data": {
                "id": config.id,
                "agent_type": config.agent_type,
                "agent_name": config.agent_name,
                "model_provider": config.model_provider,
                "model_name": config.model_name,
                "prompt_template": config.prompt_template,
                "model_params": config.model_params,
                "knowledge_bases": config.knowledge_bases or [],
                "scripts": config.scripts or [],
                "is_default": config.is_default,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update agent config: {str(e)}"
        )


@router.post("/{agent_type}/reset")
async def reset_agent_config(
    agent_type: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset agent configuration to default
    
    Restores the default configuration for the specified agent type
    """
    try:
        # Validate agent type
        valid_types = ['requirement', 'scenario', 'case', 'code', 'quality']
        if agent_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type. Must be one of: {', '.join(valid_types)}"
            )
        
        stmt = select(AgentConfig).where(AgentConfig.agent_type == agent_type)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration for agent type '{agent_type}' not found"
            )
        
        # Load default prompt template from file
        from app.services.prompt_manager import prompt_manager
        default_prompt = prompt_manager.get_prompt(f"{agent_type}_agent") or ""
        
        # Get default configuration
        default_configs = {
            'requirement': {
                'agent_name': 'Requirement Analysis Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': default_prompt,
                'model_params': {'temperature': 0.7, 'max_tokens': 2000},
                'knowledge_bases': [],
                'scripts': []
            },
            'scenario': {
                'agent_name': 'Scenario Generation Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': default_prompt,
                'model_params': {'temperature': 0.8, 'max_tokens': 2000},
                'knowledge_bases': [],
                'scripts': []
            },
            'case': {
                'agent_name': 'Test Case Generation Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': default_prompt,
                'model_params': {'temperature': 0.7, 'max_tokens': 3000},
                'knowledge_bases': [],
                'scripts': []
            },
            'code': {
                'agent_name': 'Code Generation Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': default_prompt,
                'model_params': {'temperature': 0.5, 'max_tokens': 4000},
                'knowledge_bases': [],
                'scripts': []
            },
            'quality': {
                'agent_name': 'Quality Analysis Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': default_prompt,
                'model_params': {'temperature': 0.6, 'max_tokens': 2000},
                'knowledge_bases': [],
                'scripts': []
            }
        }
        
        default = default_configs.get(agent_type)
        if not default:
            raise HTTPException(
                status_code=500,
                detail=f"Default configuration for '{agent_type}' not found"
            )
        
        # Reset to default
        config.agent_name = default['agent_name']
        config.model_provider = default['model_provider']
        config.model_name = default['model_name']
        config.prompt_template = default['prompt_template']
        config.model_params = default['model_params']
        config.knowledge_bases = default['knowledge_bases']
        config.scripts = default['scripts']
        config.is_default = True
        config.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(config)
        
        return {
            "success": True,
            "message": f"Agent configuration for '{agent_type}' reset to default",
            "data": {
                "id": config.id,
                "agent_type": config.agent_type,
                "agent_name": config.agent_name,
                "model_provider": config.model_provider,
                "model_name": config.model_name,
                "prompt_template": config.prompt_template,
                "model_params": config.model_params,
                "knowledge_bases": config.knowledge_bases or [],
                "scripts": config.scripts or [],
                "is_default": config.is_default,
                "updated_at": config.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset agent config: {str(e)}"
        )
