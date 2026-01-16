"""WebSocket API for Streaming Output"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from enum import Enum

from app.agents import (
    RequirementAgent,
    ScenarioAgent,
    CaseAgent,
    CodeAgent,
    QualityAgent,
    OptimizeAgent,
)
from app.services import SessionManager, DocumentParser, KnowledgeBaseService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


class MessageType(str, Enum):
    """WebSocket message types"""
    CHUNK = "chunk"
    DONE = "done"
    ERROR = "error"
    PROGRESS = "progress"


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_chunk(self, session_id: str, content: str, agent: str, step: str):
        """Send content chunk"""
        await self.send_message(session_id, {
            "type": MessageType.CHUNK,
            "content": content,
            "metadata": {
                "agent": agent,
                "step": step,
            }
        })
    
    async def send_progress(self, session_id: str, progress: int, agent: str, step: str):
        """Send progress update"""
        await self.send_message(session_id, {
            "type": MessageType.PROGRESS,
            "metadata": {
                "agent": agent,
                "step": step,
                "progress": progress,
            }
        })
    
    async def send_done(self, session_id: str, agent: str, step: str):
        """Send completion message"""
        await self.send_message(session_id, {
            "type": MessageType.DONE,
            "metadata": {
                "agent": agent,
                "step": step,
            }
        })
    
    async def send_error(self, session_id: str, error: str, agent: str, step: str):
        """Send error message"""
        await self.send_message(session_id, {
            "type": MessageType.ERROR,
            "error": error,
            "metadata": {
                "agent": agent,
                "step": step,
            }
        })


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """
    WebSocket endpoint for streaming generation output
    
    Expected message format:
    {
        "action": "requirement" | "scenario" | "case" | "code" | "quality" | "optimize" | "supplement",
        "session_id": "uuid",
        "data": {...}  # Action-specific data
    }
    """
    session_id = None
    
    try:
        # Accept connection
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        
        # Wait for initial message
        message = await websocket.receive_json()
        action = message.get("action")
        session_id = message.get("session_id")
        data = message.get("data", {})
        
        if not action or not session_id:
            await websocket.send_json({
                "type": MessageType.ERROR,
                "error": "Missing action or session_id",
            })
            await websocket.close()
            return
        
        # Register connection
        manager.active_connections[session_id] = websocket
        
        # Initialize services
        from app.core.redis_client import get_redis
        redis = await get_redis()
        session_manager = SessionManager(redis)
        
        # Route to appropriate handler
        if action == "requirement":
            await handle_requirement_stream(session_id, data, session_manager)
        elif action == "scenario":
            await handle_scenario_stream(session_id, data, session_manager)
        elif action == "case":
            await handle_case_stream(session_id, data, session_manager)
        elif action == "code":
            await handle_code_stream(session_id, data, session_manager)
        elif action == "quality":
            await handle_quality_stream(session_id, data, session_manager)
        elif action == "optimize":
            await handle_optimize_stream(session_id, data, session_manager)
        elif action == "supplement":
            await handle_supplement_stream(session_id, data, session_manager)
        else:
            await manager.send_error(session_id, f"Unknown action: {action}", "system", action)
        
        # Keep connection alive until client disconnects
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if session_id:
            await manager.send_error(session_id, str(e), "system", "error")
    finally:
        if session_id:
            manager.disconnect(session_id)


async def handle_requirement_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle requirement analysis with streaming"""
    try:
        await manager.send_progress(session_id, 10, "requirement", "start")
        
        # Extract requirement text
        requirement_text = data.get("requirement_text", "")
        test_type = data.get("test_type", "ui")
        kb_ids = data.get("knowledge_base_ids", [])
        
        # Retrieve knowledge base context
        kb_context = ""
        if kb_ids:
            await manager.send_progress(session_id, 20, "requirement", "kb_search")
            # Need DB session for KnowledgeBaseService
            from app.core.database import get_async_session
            async with get_async_session() as db:
                kb_service = KnowledgeBaseService(db)
                try:
                    kb_results = await kb_service.search(requirement_text, "rule", limit=3)
                    if kb_results:
                        kb_context = "\n\n".join([
                            f"参考文档 {i+1}:\n{result['content']}"
                            for i, result in enumerate(kb_results)
                        ])
                except Exception as e:
                    logger.warning(f"Failed to retrieve knowledge base: {e}")
        
        await manager.send_progress(session_id, 40, "requirement", "analyzing")
        
        # Initialize agent with streaming callback
        agent = RequirementAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "requirement", "analyzing")
        
        # Analyze with streaming
        result = await agent.analyze(
            requirement_text=requirement_text,
            test_type=test_type,
            knowledge_context=kb_context,
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "requirement", "saving")
        
        # Save result
        await session_manager.save_step_result(session_id, "requirement_analysis", result)
        
        await manager.send_progress(session_id, 100, "requirement", "complete")
        await manager.send_done(session_id, "requirement", "complete")
        
    except Exception as e:
        logger.error(f"Requirement stream error: {e}")
        await manager.send_error(session_id, str(e), "requirement", "error")


async def handle_scenario_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle scenario generation with streaming"""
    try:
        await manager.send_progress(session_id, 10, "scenario", "start")
        
        requirement_analysis = data.get("requirement_analysis", {})
        test_type = data.get("test_type", "ui")
        
        await manager.send_progress(session_id, 30, "scenario", "generating")
        
        # Initialize agent
        agent = ScenarioAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "scenario", "generating")
        
        # Generate scenarios
        result = await agent.generate(
            requirement_analysis=requirement_analysis,
            test_type=test_type,
            defect_history="",
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "scenario", "saving")
        
        # Save result
        await session_manager.save_step_result(session_id, "scenarios", result)
        
        await manager.send_progress(session_id, 100, "scenario", "complete")
        await manager.send_done(session_id, "scenario", "complete")
        
    except Exception as e:
        logger.error(f"Scenario stream error: {e}")
        await manager.send_error(session_id, str(e), "scenario", "error")


async def handle_case_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle case generation with streaming"""
    try:
        await manager.send_progress(session_id, 10, "case", "start")
        
        scenarios = data.get("scenarios", [])
        
        await manager.send_progress(session_id, 30, "case", "generating")
        
        # Initialize agent
        agent = CaseAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "case", "generating")
        
        # Generate cases
        result = await agent.generate(
            scenarios=scenarios,
            template_id=None,
            script_ids=[],
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "case", "saving")
        
        # Save result
        await session_manager.save_step_result(session_id, "cases", result)
        
        await manager.send_progress(session_id, 100, "case", "complete")
        await manager.send_done(session_id, "case", "complete")
        
    except Exception as e:
        logger.error(f"Case stream error: {e}")
        await manager.send_error(session_id, str(e), "case", "error")


async def handle_code_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle code generation with streaming"""
    try:
        await manager.send_progress(session_id, 10, "code", "start")
        
        test_cases = data.get("test_cases", [])
        tech_stack = data.get("tech_stack")
        use_default_stack = data.get("use_default_stack", True)
        
        await manager.send_progress(session_id, 30, "code", "generating")
        
        # Initialize agent
        agent = CodeAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "code", "generating")
        
        # Generate code
        result = await agent.generate(
            test_cases=test_cases,
            tech_stack=tech_stack,
            use_default_stack=use_default_stack,
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "code", "saving")
        
        # Save result
        await session_manager.save_step_result(session_id, "code", result)
        
        await manager.send_progress(session_id, 100, "code", "complete")
        await manager.send_done(session_id, "code", "complete")
        
    except Exception as e:
        logger.error(f"Code stream error: {e}")
        await manager.send_error(session_id, str(e), "code", "error")


async def handle_quality_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle quality analysis with streaming"""
    try:
        await manager.send_progress(session_id, 10, "quality", "start")
        
        requirement_analysis = data.get("requirement_analysis", {})
        scenarios = data.get("scenarios", [])
        test_cases = data.get("test_cases", [])
        
        await manager.send_progress(session_id, 30, "quality", "analyzing")
        
        # Initialize agent
        agent = QualityAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "quality", "analyzing")
        
        # Analyze quality
        result = await agent.analyze(
            requirement_analysis=requirement_analysis,
            scenarios=scenarios,
            test_cases=test_cases,
            defect_history="",
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "quality", "saving")
        
        # Save result
        await session_manager.save_step_result(session_id, "quality_report", result)
        
        await manager.send_progress(session_id, 100, "quality", "complete")
        await manager.send_done(session_id, "quality", "complete")
        
    except Exception as e:
        logger.error(f"Quality stream error: {e}")
        await manager.send_error(session_id, str(e), "quality", "error")


async def handle_optimize_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle case optimization with streaming"""
    try:
        await manager.send_progress(session_id, 10, "optimize", "start")
        
        selected_cases = data.get("selected_cases", [])
        instruction = data.get("instruction", "")
        
        await manager.send_progress(session_id, 30, "optimize", "optimizing")
        
        # Initialize agent
        agent = OptimizeAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "optimize", "optimizing")
        
        # Optimize cases
        result = await agent.optimize(
            selected_cases=selected_cases,
            instruction=instruction,
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "optimize", "saving")
        
        # Update conversation history
        conversation = await session_manager.get_step_result(session_id, "conversation") or []
        conversation.append({
            "type": "optimize",
            "instruction": instruction,
            "result": result,
        })
        await session_manager.save_step_result(session_id, "conversation", conversation)
        
        await manager.send_progress(session_id, 100, "optimize", "complete")
        await manager.send_done(session_id, "optimize", "complete")
        
    except Exception as e:
        logger.error(f"Optimize stream error: {e}")
        await manager.send_error(session_id, str(e), "optimize", "error")


async def handle_supplement_stream(session_id: str, data: Dict[str, Any], session_manager: SessionManager):
    """Handle case supplement with streaming"""
    try:
        await manager.send_progress(session_id, 10, "supplement", "start")
        
        existing_cases = data.get("existing_cases", [])
        requirement = data.get("requirement", "")
        
        await manager.send_progress(session_id, 30, "supplement", "supplementing")
        
        # Initialize agent
        agent = OptimizeAgent()
        
        async def stream_callback(chunk: str):
            await manager.send_chunk(session_id, chunk, "supplement", "supplementing")
        
        # Supplement cases
        result = await agent.supplement(
            existing_cases=existing_cases,
            requirement=requirement,
            stream_callback=stream_callback,
        )
        
        await manager.send_progress(session_id, 90, "supplement", "saving")
        
        # Update conversation history
        conversation = await session_manager.get_step_result(session_id, "conversation") or []
        conversation.append({
            "type": "supplement",
            "requirement": requirement,
            "result": result,
        })
        await session_manager.save_step_result(session_id, "conversation", conversation)
        
        await manager.send_progress(session_id, 100, "supplement", "complete")
        await manager.send_done(session_id, "supplement", "complete")
        
    except Exception as e:
        logger.error(f"Supplement stream error: {e}")
        await manager.send_error(session_id, str(e), "supplement", "error")
