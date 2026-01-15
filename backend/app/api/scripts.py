"""Python Script Management API"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.python_script import PythonScript
from app.services.script_executor import ScriptExecutor
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/scripts", tags=["scripts"])

# Initialize script executor
script_executor = ScriptExecutor()


# Request/Response Models
class ScriptCreateRequest(BaseModel):
    """Request model for creating a script"""
    name: str
    description: Optional[str] = None
    code: str


class ScriptUpdateRequest(BaseModel):
    """Request model for updating a script"""
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None


class ScriptTestRequest(BaseModel):
    """Request model for testing a script"""
    args: Optional[dict] = None


class ScriptResponse(BaseModel):
    """Response model for script"""
    id: int
    name: str
    description: Optional[str]
    code: str
    dependencies: List[str]
    is_builtin: bool
    created_at: datetime
    updated_at: datetime


@router.post("")
async def create_script(
    request: ScriptCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new Python script
    
    The script will be validated and dependencies will be extracted automatically
    """
    try:
        # Check if script name already exists
        stmt = select(PythonScript).where(PythonScript.name == request.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Script with name '{request.name}' already exists"
            )
        
        # Validate script syntax
        if not script_executor.validate_script(request.code):
            raise HTTPException(
                status_code=400,
                detail="Invalid Python syntax"
            )
        
        # Extract dependencies
        dependencies = script_executor.extract_dependencies(request.code)
        
        # Create script
        script = PythonScript(
            name=request.name,
            description=request.description,
            code=request.code,
            dependencies=dependencies,
            is_builtin=False
        )
        
        db.add(script)
        await db.commit()
        await db.refresh(script)
        
        return {
            "success": True,
            "message": "Script created successfully",
            "data": {
                "id": script.id,
                "name": script.name,
                "description": script.description,
                "dependencies": script.dependencies,
                "created_at": script.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create script: {str(e)}"
        )


@router.get("")
async def list_scripts(
    include_builtin: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all Python scripts
    
    Supports filtering built-in scripts and pagination
    """
    try:
        stmt = select(PythonScript).order_by(
            PythonScript.is_builtin.desc(),
            PythonScript.created_at.desc()
        )
        
        if not include_builtin:
            stmt = stmt.where(PythonScript.is_builtin == False)
        
        stmt = stmt.offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        scripts = result.scalars().all()
        
        # Format response
        data = []
        for script in scripts:
            data.append({
                "id": script.id,
                "name": script.name,
                "description": script.description,
                "dependencies": script.dependencies,
                "is_builtin": script.is_builtin,
                "created_at": script.created_at.isoformat(),
                "updated_at": script.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list scripts: {str(e)}"
        )


@router.get("/{script_id}")
async def get_script(
    script_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get script by ID
    
    Returns detailed information including code
    """
    try:
        stmt = select(PythonScript).where(PythonScript.id == script_id)
        result = await db.execute(stmt)
        script = result.scalar_one_or_none()
        
        if not script:
            raise HTTPException(
                status_code=404,
                detail=f"Script {script_id} not found"
            )
        
        return {
            "success": True,
            "data": {
                "id": script.id,
                "name": script.name,
                "description": script.description,
                "code": script.code,
                "dependencies": script.dependencies,
                "is_builtin": script.is_builtin,
                "created_at": script.created_at.isoformat(),
                "updated_at": script.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get script: {str(e)}"
        )


@router.put("/{script_id}")
async def update_script(
    script_id: int,
    request: ScriptUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a script
    
    Built-in scripts cannot be updated
    """
    try:
        stmt = select(PythonScript).where(PythonScript.id == script_id)
        result = await db.execute(stmt)
        script = result.scalar_one_or_none()
        
        if not script:
            raise HTTPException(
                status_code=404,
                detail=f"Script {script_id} not found"
            )
        
        if script.is_builtin:
            raise HTTPException(
                status_code=403,
                detail="Built-in scripts cannot be updated"
            )
        
        # Update fields
        if request.name is not None:
            # Check if new name conflicts
            stmt = select(PythonScript).where(
                PythonScript.name == request.name,
                PythonScript.id != script_id
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Script with name '{request.name}' already exists"
                )
            
            script.name = request.name
        
        if request.description is not None:
            script.description = request.description
        
        if request.code is not None:
            # Validate new code
            if not script_executor.validate_script(request.code):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Python syntax"
                )
            
            script.code = request.code
            script.dependencies = script_executor.extract_dependencies(request.code)
        
        script.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(script)
        
        return {
            "success": True,
            "message": "Script updated successfully",
            "data": {
                "id": script.id,
                "name": script.name,
                "description": script.description,
                "dependencies": script.dependencies,
                "updated_at": script.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update script: {str(e)}"
        )


@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a script
    
    Built-in scripts cannot be deleted
    """
    try:
        stmt = select(PythonScript).where(PythonScript.id == script_id)
        result = await db.execute(stmt)
        script = result.scalar_one_or_none()
        
        if not script:
            raise HTTPException(
                status_code=404,
                detail=f"Script {script_id} not found"
            )
        
        if script.is_builtin:
            raise HTTPException(
                status_code=403,
                detail="Built-in scripts cannot be deleted"
            )
        
        await db.delete(script)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Script {script_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete script: {str(e)}"
        )


@router.post("/{script_id}/test")
async def test_script(
    script_id: int,
    request: ScriptTestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Test execute a script
    
    Runs the script in a sandbox environment with optional arguments
    """
    try:
        stmt = select(PythonScript).where(PythonScript.id == script_id)
        result = await db.execute(stmt)
        script = result.scalar_one_or_none()
        
        if not script:
            raise HTTPException(
                status_code=404,
                detail=f"Script {script_id} not found"
            )
        
        # Execute script
        exec_result = script_executor.execute(script.code, timeout=30)
        
        return {
            "success": exec_result["success"],
            "output": exec_result.get("output"),
            "error": exec_result.get("error"),
            "execution_time": exec_result.get("execution_time")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test script: {str(e)}"
        )
