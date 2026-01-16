"""Agent Prompts Management API"""

from typing import Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.prompt_manager import prompt_manager


router = APIRouter(prefix="/prompts", tags=["prompts"])


class PromptUpdate(BaseModel):
    """Prompt update request"""
    prompt: str


class PromptResponse(BaseModel):
    """Prompt response"""
    agent_type: str
    prompt: str


class PromptsListResponse(BaseModel):
    """List of prompts response"""
    prompts: Dict[str, str]


@router.get("/", response_model=PromptsListResponse)
async def list_prompts():
    """
    List all agent prompts.
    
    Returns:
        Dict mapping agent type to prompt text
    """
    prompts = prompt_manager.list_prompts()
    return {"prompts": prompts}


@router.get("/{agent_type}", response_model=PromptResponse)
async def get_prompt(agent_type: str):
    """
    Get prompt for specific agent type.
    
    Args:
        agent_type: Agent type (requirement/scenario/case/code/quality/optimize)
        
    Returns:
        Prompt text
        
    Raises:
        404: If prompt not found
    """
    prompt = prompt_manager.get_prompt(f"{agent_type}_agent")
    if prompt is None:
        raise HTTPException(status_code=404, detail=f"Prompt not found for agent type: {agent_type}")
    
    return {
        "agent_type": agent_type,
        "prompt": prompt
    }


@router.put("/{agent_type}", response_model=PromptResponse)
async def update_prompt(agent_type: str, request: PromptUpdate):
    """
    Update prompt for specific agent type.
    
    Args:
        agent_type: Agent type
        request: Prompt update request
        
    Returns:
        Updated prompt
        
    Raises:
        500: If update fails
    """
    success = prompt_manager.set_prompt(f"{agent_type}_agent", request.prompt)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update prompt")
    
    return {
        "agent_type": agent_type,
        "prompt": request.prompt
    }


@router.post("/reload")
async def reload_prompts():
    """
    Reload all prompts from disk.
    
    Returns:
        Success message
    """
    prompt_manager.reload_prompts()
    return {"message": "Prompts reloaded successfully"}
