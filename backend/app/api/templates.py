"""Test Case Template Management API"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.case_template import CaseTemplate
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


# Request/Response Models
class TemplateCreateRequest(BaseModel):
    """Request model for creating a template"""
    name: str
    test_type: str  # ui/api/unit
    template_structure: dict


class TemplateUpdateRequest(BaseModel):
    """Request model for updating a template"""
    name: Optional[str] = None
    test_type: Optional[str] = None
    template_structure: Optional[dict] = None


class TemplateResponse(BaseModel):
    """Response model for template"""
    id: int
    name: str
    test_type: str
    template_structure: dict
    is_builtin: bool
    created_at: datetime
    updated_at: datetime


@router.post("")
async def create_template(
    request: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new test case template
    
    Templates define the structure and fields for test cases
    """
    try:
        # Validate test type
        valid_types = ['ui', 'api', 'unit']
        if request.test_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid test type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Check if template name already exists
        stmt = select(CaseTemplate).where(CaseTemplate.name == request.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Template with name '{request.name}' already exists"
            )
        
        # Validate template structure
        required_fields = ['case_id', 'title', 'test_type', 'priority']
        for field in required_fields:
            if field not in request.template_structure:
                raise HTTPException(
                    status_code=400,
                    detail=f"Template structure must include '{field}' field"
                )
        
        # Create template
        template = CaseTemplate(
            name=request.name,
            test_type=request.test_type,
            template_structure=request.template_structure,
            is_builtin=False
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        return {
            "success": True,
            "message": "Template created successfully",
            "data": {
                "id": template.id,
                "name": template.name,
                "test_type": template.test_type,
                "template_structure": template.template_structure,
                "created_at": template.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create template: {str(e)}"
        )


@router.get("")
async def list_templates(
    test_type: Optional[str] = None,
    include_builtin: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all test case templates
    
    Supports filtering by test type and pagination
    """
    try:
        stmt = select(CaseTemplate).order_by(
            CaseTemplate.is_builtin.desc(),
            CaseTemplate.created_at.desc()
        )
        
        if test_type:
            valid_types = ['ui', 'api', 'unit']
            if test_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid test type. Must be one of: {', '.join(valid_types)}"
                )
            stmt = stmt.where(CaseTemplate.test_type == test_type)
        
        if not include_builtin:
            stmt = stmt.where(CaseTemplate.is_builtin == False)
        
        stmt = stmt.offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        templates = result.scalars().all()
        
        # Format response
        data = []
        for template in templates:
            data.append({
                "id": template.id,
                "name": template.name,
                "test_type": template.test_type,
                "is_builtin": template.is_builtin,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get template by ID
    
    Returns detailed information including template structure
    """
    try:
        stmt = select(CaseTemplate).where(CaseTemplate.id == template_id)
        result = await db.execute(stmt)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} not found"
            )
        
        return {
            "success": True,
            "data": {
                "id": template.id,
                "name": template.name,
                "test_type": template.test_type,
                "template_structure": template.template_structure,
                "is_builtin": template.is_builtin,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template: {str(e)}"
        )


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    request: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a template
    
    Built-in templates cannot be updated
    """
    try:
        stmt = select(CaseTemplate).where(CaseTemplate.id == template_id)
        result = await db.execute(stmt)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} not found"
            )
        
        if template.is_builtin:
            raise HTTPException(
                status_code=403,
                detail="Built-in templates cannot be updated"
            )
        
        # Update fields
        if request.name is not None:
            # Check if new name conflicts
            stmt = select(CaseTemplate).where(
                CaseTemplate.name == request.name,
                CaseTemplate.id != template_id
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Template with name '{request.name}' already exists"
                )
            
            template.name = request.name
        
        if request.test_type is not None:
            valid_types = ['ui', 'api', 'unit']
            if request.test_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid test type. Must be one of: {', '.join(valid_types)}"
                )
            template.test_type = request.test_type
        
        if request.template_structure is not None:
            # Validate template structure
            required_fields = ['case_id', 'title', 'test_type', 'priority']
            for field in required_fields:
                if field not in request.template_structure:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Template structure must include '{field}' field"
                    )
            template.template_structure = request.template_structure
        
        template.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(template)
        
        return {
            "success": True,
            "message": "Template updated successfully",
            "data": {
                "id": template.id,
                "name": template.name,
                "test_type": template.test_type,
                "template_structure": template.template_structure,
                "updated_at": template.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a template
    
    Built-in templates cannot be deleted
    """
    try:
        stmt = select(CaseTemplate).where(CaseTemplate.id == template_id)
        result = await db.execute(stmt)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} not found"
            )
        
        if template.is_builtin:
            raise HTTPException(
                status_code=403,
                detail="Built-in templates cannot be deleted"
            )
        
        await db.delete(template)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Template {template_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete template: {str(e)}"
        )
