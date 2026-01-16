"""Feedback API Endpoints

用于记录用户对 Agent 执行结果的反馈。
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.agent_execution import AgentExecution

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])


class ExecutionFeedbackRequest(BaseModel):
    """执行反馈请求"""
    accepted: bool
    modified: bool = False
    modifications: Optional[Dict[str, Any]] = None


@router.post("/execution/{execution_id}")
async def record_execution_feedback(
    execution_id: str,
    feedback: ExecutionFeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """记录用户对 Agent 执行结果的反馈
    
    Args:
        execution_id: 执行 ID
        feedback: 反馈信息
        db: 数据库会话
        
    Returns:
        操作结果
    """
    try:
        # 查找执行记录
        stmt = select(AgentExecution).where(AgentExecution.execution_id == execution_id)
        result = await db.execute(stmt)
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # 更新反馈信息
        execution.user_accepted = feedback.accepted
        execution.user_modified = feedback.modified
        execution.modification_details = feedback.modifications
        
        await db.commit()
        
        logger.info(f"Recorded feedback for execution: {execution_id}")
        
        return {
            "status": "success",
            "execution_id": execution_id,
            "feedback": {
                "accepted": feedback.accepted,
                "modified": feedback.modified
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record feedback: {str(e)}"
        )


@router.get("/execution/{execution_id}")
async def get_execution_feedback(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取执行反馈信息
    
    Args:
        execution_id: 执行 ID
        db: 数据库会话
        
    Returns:
        反馈信息
    """
    try:
        # 查找执行记录
        stmt = select(AgentExecution).where(AgentExecution.execution_id == execution_id)
        result = await db.execute(stmt)
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "execution_id": execution_id,
            "agent_type": execution.agent_type,
            "feedback": {
                "accepted": execution.user_accepted,
                "modified": execution.user_modified,
                "modifications": execution.modification_details
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feedback: {str(e)}"
        )


@router.get("/session/{session_id}/executions")
async def get_session_executions(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话的所有执行记录
    
    Args:
        session_id: 会话 ID
        db: 数据库会话
        
    Returns:
        执行记录列表
    """
    try:
        stmt = select(AgentExecution).where(
            AgentExecution.session_id == session_id
        ).order_by(AgentExecution.created_at)
        
        result = await db.execute(stmt)
        executions = result.scalars().all()
        
        return {
            "session_id": session_id,
            "count": len(executions),
            "executions": [execution.to_dict() for execution in executions]
        }
        
    except Exception as e:
        logger.error(f"Failed to get session executions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session executions: {str(e)}"
        )
