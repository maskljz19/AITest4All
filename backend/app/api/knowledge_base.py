"""Knowledge Base Management API"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
import os
from datetime import datetime
import json

from app.services.knowledge_base import KnowledgeBaseService
from app.services.document_parser import DocumentParser
from app.core.database import get_db
from app.core.security import FileSecurityValidator

router = APIRouter(prefix="/api/v1/knowledge-base", tags=["knowledge-base"])

# Initialize document parser
doc_parser = DocumentParser()


# Request/Response Models
class KnowledgeBaseUrlRequest(BaseModel):
    """Request model for adding URL to knowledge base"""
    url: HttpUrl
    name: str
    type: str  # case/defect/rule/api
    metadata: Optional[dict] = None


class KnowledgeBaseResponse(BaseModel):
    """Response model for knowledge base item"""
    id: int
    name: str
    type: str
    storage_type: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseSearchResult(BaseModel):
    """Search result model"""
    id: int
    name: str
    type: str
    content: str
    rank: float


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    type: str = Query(..., description="Document type: case/defect/rule/api"),
    metadata: Optional[str] = Query(None, description="JSON metadata"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document to knowledge base
    
    Supports: Word, PDF, Markdown, Excel, TXT
    Max file size: 10MB
    """
    kb_service = KnowledgeBaseService(db)
    
    try:
        # Validate file upload security
        is_valid, error, sanitized_name = await FileSecurityValidator.validate_upload(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Update filename with sanitized version
        original_filename = file.filename
        file.filename = sanitized_name
        
        # Parse metadata if provided
        meta_dict = None
        if metadata:
            try:
                meta_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON metadata"
                )
        
        # Upload to knowledge base
        result = await kb_service.upload_document(
            file=file,
            kb_type=type,
            name=name or original_filename,
            metadata=meta_dict
        )
        
        return {
            "success": True,
            "message": "Document uploaded successfully",
            "data": {
                "id": result.id,
                "name": result.name,
                "type": result.type,
                "storage_type": result.storage_type,
                "created_at": result.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.post("/url")
async def add_url(request: KnowledgeBaseUrlRequest, db: AsyncSession = Depends(get_db)):
    """
    Add a URL to knowledge base
    
    The system will download and parse the content from the URL
    """
    kb_service = KnowledgeBaseService(db)
    
    try:
        # Add URL to knowledge base
        result = await kb_service.add_url(
            url=str(request.url),
            kb_type=request.type,
            name=request.name,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "message": "URL added successfully",
            "data": {
                "id": result.id,
                "name": result.name,
                "type": result.type,
                "storage_type": result.storage_type,
                "url": result.url,
                "created_at": result.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add URL: {str(e)}"
        )


@router.get("/list")
async def list_knowledge_bases(
    type: Optional[str] = Query(None, description="Filter by type: case/defect/rule/api"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    List all knowledge base items
    
    Supports filtering by type and pagination
    """
    kb_service = KnowledgeBaseService(db)
    
    try:
        if type:
            items = await kb_service.list_by_type(kb_type=type, skip=offset, limit=limit)
        else:
            items = await kb_service.list_all(skip=offset, limit=limit)
        
        # Format response
        data = []
        for item in items:
            data.append({
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "storage_type": item.storage_type,
                "file_path": item.file_path,
                "url": item.url,
                "metadata": item.metadata,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list knowledge bases: {str(e)}"
        )


@router.get("/{kb_id}")
async def get_knowledge_base(kb_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get knowledge base item by ID
    
    Returns detailed information including content
    """
    kb_service = KnowledgeBaseService(db)
    
    try:
        item = await kb_service.get_by_id(kb_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base item {kb_id} not found"
            )
        
        return {
            "success": True,
            "data": {
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "storage_type": item.storage_type,
                "file_path": item.file_path,
                "url": item.url,
                "content": item.content,
                "metadata": item.metadata,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get knowledge base: {str(e)}"
        )


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete knowledge base item by ID
    
    This will remove the item from database and delete associated files
    """
    kb_service = KnowledgeBaseService(db)
    
    try:
        # Check if item exists
        item = await kb_service.get_by_id(kb_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base item {kb_id} not found"
            )
        
        # Delete the item
        await kb_service.delete(kb_id)
        
        return {
            "success": True,
            "message": f"Knowledge base item {kb_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete knowledge base: {str(e)}"
        )


@router.get("/search")
async def search_knowledge_base(
    query: str = Query(..., min_length=1, description="Search query"),
    type: Optional[str] = Query(None, description="Filter by type: case/defect/rule/api"),
    limit: int = Query(5, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Search knowledge base using full-text search
    
    Uses PostgreSQL full-text search for efficient keyword matching
    """
    kb_service = KnowledgeBaseService(db)
    
    try:
        results = await kb_service.search(
            query=query,
            kb_type=type,
            limit=limit
        )
        
        return {
            "success": True,
            "data": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search knowledge base: {str(e)}"
        )
