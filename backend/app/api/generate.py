"""Generation API Endpoints"""

import uuid
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.schemas import (
    RequirementAnalysisRequest,
    RequirementAnalysisResponse,
    ScenarioGenerationRequest,
    ScenarioGenerationResponse,
    CaseGenerationRequest,
    CaseGenerationResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
    QualityAnalysisRequest,
    QualityAnalysisResponse,
    OptimizeRequest,
    OptimizeResponse,
    SupplementRequest,
    SupplementResponse,
    ErrorResponse,
    TestType,
)
from app.agents import factory
from app.services import (
    DocumentParser,
    DocumentParseError,
    SessionManager,
    SessionError,
    KnowledgeBaseService,
)
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/generate", tags=["generate"])


# Dependency to get services
async def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    from app.core.redis_client import get_redis
    redis = await get_redis()
    return SessionManager(redis)


def get_document_parser() -> DocumentParser:
    """Get document parser instance"""
    return DocumentParser()


async def get_knowledge_base_service(db: AsyncSession = Depends(get_db)) -> KnowledgeBaseService:
    """Get knowledge base service instance"""
    return KnowledgeBaseService(db)


async def ensure_session_exists(session_id: str, session_manager: SessionManager) -> None:
    """
    Ensure session exists, create if not found.
    For single-user scenarios, auto-create expired sessions.
    
    Args:
        session_id: Session ID to check
        session_manager: SessionManager instance
    """
    metadata = await session_manager.get_metadata(session_id)
    if not metadata:
        # Auto-create session for single-user scenario
        metadata = {
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat(),
            'current_step': None,
            'steps_completed': []
        }
        await session_manager.save_metadata(session_id, metadata)
        logger.info(f"Auto-created session: {session_id}")


@router.post(
    "/requirement",
    response_model=RequirementAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def analyze_requirement(
    requirement_text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    test_type: TestType = Form(...),
    knowledge_base_ids: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    session_manager: SessionManager = Depends(get_session_manager),
    doc_parser: DocumentParser = Depends(get_document_parser),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    """
    Analyze requirement document and extract test information
    
    Supports three input methods:
    1. File upload (Word/PDF/Markdown/Excel/TXT)
    2. URL input
    3. Direct text input
    """
    try:
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
            await session_manager.create_session(session_id)
        
        # Extract requirement text
        req_text = None
        
        if file:
            # Parse uploaded file
            try:
                content = await file.read()
                req_text = doc_parser.extract_text(content, file.filename)
            except DocumentParseError as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "DOCUMENT_PARSE_ERROR",
                        "message": f"Failed to parse document: {str(e)}",
                    }
                )
        elif url:
            # Parse URL content
            try:
                req_text = doc_parser.parse_url(url)
            except DocumentParseError as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "DOCUMENT_PARSE_ERROR",
                        "message": f"Failed to parse URL: {str(e)}",
                    }
                )
        elif requirement_text:
            req_text = requirement_text
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INVALID_INPUT",
                    "message": "Must provide file, url, or requirement_text",
                }
            )
        
        # Parse knowledge base IDs
        kb_ids = []
        if knowledge_base_ids:
            try:
                kb_ids = [int(id.strip()) for id in knowledge_base_ids.split(",")]
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_INPUT",
                        "message": "Invalid knowledge_base_ids format",
                    }
                )
        
        # Retrieve knowledge base context
        kb_context = ""
        if kb_ids:
            try:
                kb_results = await kb_service.search(req_text, "rule", limit=3)
                if kb_results:
                    kb_context = "\n\n".join([
                        f"参考文档 {i+1}:\n{result['content']}"
                        for i, result in enumerate(kb_results)
                    ])
            except Exception as e:
                logger.warning(f"Failed to retrieve knowledge base: {e}")
                # Continue without knowledge base
        
        # Initialize requirement agent
        agent = await factory.create_requirement_agent_async()
        
        # Analyze requirement
        try:
            result = await agent.analyze(
                requirement_text=req_text,
                test_type=test_type.value,
                knowledge_context=kb_context,
            )
        except Exception as e:
            logger.error(f"Requirement analysis failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to analyze requirement: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Save result to session
        await session_manager.save_step_result(
            session_id,
            "requirement_analysis",
            result
        )
        
        return RequirementAnalysisResponse(
            session_id=session_id,
            **result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in requirement analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )



@router.post(
    "/scenario",
    response_model=ScenarioGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def generate_scenarios(
    request: ScenarioGenerationRequest,
    session_manager: SessionManager = Depends(get_session_manager),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    """
    Generate test scenarios based on requirement analysis
    """
    try:
        # Ensure session exists (auto-create if needed)
        await ensure_session_exists(request.session_id, session_manager)
        
        # Retrieve defect history from knowledge base
        defect_context = ""
        if request.defect_kb_ids:
            try:
                # Search for relevant defects
                req_text = " ".join(request.requirement_analysis.get("function_points", []))
                defect_results = await kb_service.search(req_text, "defect", limit=5)
                if defect_results:
                    defect_context = "\n\n".join([
                        f"历史缺陷 {i+1}:\n{result['content']}"
                        for i, result in enumerate(defect_results)
                    ])
            except Exception as e:
                logger.warning(f"Failed to retrieve defect history: {e}")
        
        # Initialize scenario agent
        agent = await factory.create_scenario_agent_async()
        
        # Generate scenarios
        try:
            result = await agent.generate(
                requirement_analysis=request.requirement_analysis,
                test_type=request.test_type.value,
                defect_history=defect_context,
            )
        except Exception as e:
            logger.error(f"Scenario generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to generate scenarios: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Save result to session
        await session_manager.save_step_result(
            request.session_id,
            "scenarios",
            result
        )
        
        return ScenarioGenerationResponse(
            session_id=request.session_id,
            scenarios=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in scenario generation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )


@router.post(
    "/case",
    response_model=CaseGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def generate_cases(
    request: CaseGenerationRequest,
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    Generate detailed test cases for each scenario
    """
    try:
        # Ensure session exists (auto-create if needed)
        await ensure_session_exists(request.session_id, session_manager)
        
        # Initialize case agent
        agent = await factory.create_case_agent_async()
        
        # Generate test cases
        try:
            result = await agent.generate(
                scenarios=[s.dict() for s in request.scenarios],
                template_id=request.template_id,
                script_ids=request.script_ids or [],
            )
        except Exception as e:
            logger.error(f"Case generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to generate test cases: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Save result to session
        await session_manager.save_step_result(
            request.session_id,
            "cases",
            result
        )
        
        return CaseGenerationResponse(
            session_id=request.session_id,
            test_cases=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in case generation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )


@router.post(
    "/code",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def generate_code(
    request: CodeGenerationRequest,
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    Generate automated test code based on test cases
    
    Supports streaming response for large code generation
    """
    try:
        # Ensure session exists (auto-create if needed)
        await ensure_session_exists(request.session_id, session_manager)
        
        # Initialize code agent
        agent = await factory.create_code_agent_async()
        
        # Generate code with better error handling
        try:
            result = await agent.generate(
                test_cases=[tc.dict() for tc in request.test_cases],
                tech_stack=request.tech_stack,
                use_default_stack=request.use_default_stack,
            )
        except ValueError as e:
            # Handle JSON parsing errors
            logger.error(f"Code generation parsing error: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "CODE_PARSE_ERROR",
                    "message": f"Failed to parse generated code: {str(e)}",
                    "retry_after": 5,
                }
            )
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to generate code: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Save result to session
        await session_manager.save_step_result(
            request.session_id,
            "code",
            result
        )
        
        # Return response with proper structure
        # result should be a dict with file paths as keys and code as values
        return CodeGenerationResponse(
            session_id=request.session_id,
            files=result.get("files", result) if isinstance(result, dict) else {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in code generation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )


@router.post(
    "/quality",
    response_model=QualityAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def analyze_quality(
    request: QualityAnalysisRequest,
    session_manager: SessionManager = Depends(get_session_manager),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    """
    Analyze test case quality and provide improvement suggestions
    """
    try:
        # Ensure session exists (auto-create if needed)
        await ensure_session_exists(request.session_id, session_manager)
        
        # Retrieve defect history from knowledge base
        defect_context = ""
        if request.defect_kb_ids:
            try:
                req_text = " ".join(request.requirement_analysis.get("function_points", []))
                defect_results = await kb_service.search(req_text, "defect", limit=5)
                if defect_results:
                    defect_context = "\n\n".join([
                        f"历史缺陷 {i+1}:\n{result['content']}"
                        for i, result in enumerate(defect_results)
                    ])
            except Exception as e:
                logger.warning(f"Failed to retrieve defect history: {e}")
        
        # Initialize quality agent
        agent = await factory.create_quality_agent_async()
        
        # Analyze quality
        try:
            result = await agent.analyze(
                requirement_analysis=request.requirement_analysis,
                scenarios=[s.dict() for s in request.scenarios],
                test_cases=[tc.dict() for tc in request.test_cases],
                defect_history=defect_context,
            )
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to analyze quality: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Save result to session
        await session_manager.save_step_result(
            request.session_id,
            "quality_report",
            result
        )
        
        return QualityAnalysisResponse(
            session_id=request.session_id,
            **result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in quality analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )



@router.post(
    "/optimize",
    response_model=OptimizeResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def optimize_cases(
    request: OptimizeRequest,
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    Optimize selected test cases based on user instruction
    """
    try:
        # Ensure session exists (auto-create if needed)
        await ensure_session_exists(request.session_id, session_manager)
        
        # Initialize optimize agent
        agent = await factory.create_optimize_agent_async()
        
        # Optimize cases
        try:
            result = await agent.optimize(
                selected_cases=[tc.dict() for tc in request.selected_cases],
                instruction=request.instruction,
            )
        except Exception as e:
            logger.error(f"Case optimization failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to optimize cases: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Update conversation history in session
        conversation = await session_manager.get_step_result(request.session_id, "conversation") or []
        conversation.append({
            "type": "optimize",
            "instruction": request.instruction,
            "result": result,
        })
        await session_manager.save_step_result(
            request.session_id,
            "conversation",
            conversation
        )
        
        return OptimizeResponse(
            session_id=request.session_id,
            optimized_cases=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in case optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )


@router.post(
    "/supplement",
    response_model=SupplementResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def supplement_cases(
    request: SupplementRequest,
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    Supplement new test cases based on existing cases and requirements
    """
    try:
        # Ensure session exists (auto-create if needed)
        await ensure_session_exists(request.session_id, session_manager)
        
        # Initialize optimize agent (handles both optimize and supplement)
        agent = await factory.create_optimize_agent_async()
        
        # Supplement cases
        try:
            result = await agent.supplement(
                existing_cases=[tc.dict() for tc in request.existing_cases],
                requirement=request.requirement,
            )
        except Exception as e:
            logger.error(f"Case supplement failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "LLM_API_ERROR",
                    "message": f"Failed to supplement cases: {str(e)}",
                    "retry_after": 5,
                }
            )
        
        # Update conversation history in session
        conversation = await session_manager.get_step_result(request.session_id, "conversation") or []
        conversation.append({
            "type": "supplement",
            "requirement": request.requirement,
            "result": result,
        })
        await session_manager.save_step_result(
            request.session_id,
            "conversation",
            conversation
        )
        
        return SupplementResponse(
            session_id=request.session_id,
            new_cases=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in case supplement: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        )
