"""Knowledge Base Service

Manages knowledge base documents with PostgreSQL full-text search.
Supports document upload, indexing, and retrieval.
"""

import logging
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from app.models.knowledge_base import KnowledgeBase
from app.services.document_parser import DocumentParser, DocumentParseError
from app.core.config import settings

logger = logging.getLogger(__name__)


class KnowledgeBaseError(Exception):
    """Exception raised for knowledge base operations"""
    pass


class KnowledgeBaseService:
    """Service for managing knowledge base documents"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = DocumentParser()
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Ensure knowledge base storage directory exists"""
        storage_path = Path(settings.knowledge_base_dir)
        storage_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_document(
        self,
        file: UploadFile,
        kb_type: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeBase:
        """Upload and index a document
        
        Args:
            file: Uploaded file
            kb_type: Knowledge base type (case/defect/rule/api)
            name: Optional document name (defaults to filename)
            metadata: Optional metadata dictionary
            
        Returns:
            Created KnowledgeBase instance
            
        Raises:
            KnowledgeBaseError: If upload or parsing fails
        """
        try:
            # Validate file size
            max_size = settings.max_upload_size_mb * 1024 * 1024
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > max_size:
                raise KnowledgeBaseError(
                    f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds "
                    f"maximum allowed size ({settings.max_upload_size_mb}MB)"
                )
            
            # Generate storage path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            file_path = Path(settings.knowledge_base_dir) / kb_type / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse document content
            try:
                content = self.parser.parse_file(str(file_path))
            except DocumentParseError as e:
                # Clean up file if parsing fails
                file_path.unlink(missing_ok=True)
                raise KnowledgeBaseError(f"Failed to parse document: {str(e)}")
            
            # Create knowledge base entry
            kb = KnowledgeBase(
                name=name or file.filename,
                type=kb_type,
                storage_type='local',
                file_path=str(file_path),
                content=content,
                metadata=metadata or {}
            )
            
            self.db.add(kb)
            await self.db.commit()
            await self.db.refresh(kb)
            
            logger.info(f"Uploaded document: {kb.name} (ID: {kb.id})")
            return kb
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to upload document: {str(e)}")
            raise KnowledgeBaseError(f"Failed to upload document: {str(e)}")
    
    async def add_url(
        self,
        url: str,
        kb_type: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeBase:
        """Add a URL to knowledge base
        
        Args:
            url: URL to fetch content from
            kb_type: Knowledge base type
            name: Optional document name
            metadata: Optional metadata dictionary
            
        Returns:
            Created KnowledgeBase instance
            
        Raises:
            KnowledgeBaseError: If fetching or parsing fails
        """
        try:
            # Fetch and parse URL content
            try:
                content = self.parser.parse_url(url)
            except DocumentParseError as e:
                raise KnowledgeBaseError(f"Failed to fetch URL: {str(e)}")
            
            # Create knowledge base entry
            kb = KnowledgeBase(
                name=name or url,
                type=kb_type,
                storage_type='url',
                url=url,
                content=content,
                metadata=metadata or {}
            )
            
            self.db.add(kb)
            await self.db.commit()
            await self.db.refresh(kb)
            
            logger.info(f"Added URL: {kb.name} (ID: {kb.id})")
            return kb
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add URL: {str(e)}")
            raise KnowledgeBaseError(f"Failed to add URL: {str(e)}")
    
    async def search(
        self,
        query: str,
        kb_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search knowledge base using full-text search
        
        Args:
            query: Search query
            kb_type: Optional filter by knowledge base type
            limit: Maximum number of results
            
        Returns:
            List of search results with relevance ranking
        """
        try:
            # Build full-text search query
            # Using PostgreSQL's to_tsquery for search
            search_query = ' & '.join(query.split())
            
            # Base query with full-text search
            stmt = select(
                KnowledgeBase.id,
                KnowledgeBase.name,
                KnowledgeBase.type,
                KnowledgeBase.content,
                KnowledgeBase.metadata,
                KnowledgeBase.created_at,
                # Calculate relevance rank
                func.ts_rank(
                    KnowledgeBase.search_vector,
                    func.to_tsquery('simple', search_query)
                ).label('rank')
            ).where(
                KnowledgeBase.search_vector.op('@@')(
                    func.to_tsquery('simple', search_query)
                )
            )
            
            # Filter by type if specified
            if kb_type:
                stmt = stmt.where(KnowledgeBase.type == kb_type)
            
            # Order by relevance and limit results
            stmt = stmt.order_by(text('rank DESC')).limit(limit)
            
            result = await self.db.execute(stmt)
            rows = result.all()
            
            # Format results
            results = []
            for row in rows:
                results.append({
                    'id': row.id,
                    'name': row.name,
                    'type': row.type,
                    'content': row.content[:500] + '...' if len(row.content) > 500 else row.content,
                    'metadata': row.metadata,
                    'created_at': row.created_at.isoformat(),
                    'relevance': float(row.rank)
                })
            
            logger.info(f"Search query '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            # Return empty results on error rather than raising
            return []
    
    async def get_by_id(self, kb_id: int) -> Optional[KnowledgeBase]:
        """Get knowledge base entry by ID
        
        Args:
            kb_id: Knowledge base ID
            
        Returns:
            KnowledgeBase instance or None if not found
        """
        stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_type(
        self,
        kb_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """List knowledge base entries by type
        
        Args:
            kb_type: Knowledge base type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of KnowledgeBase instances
        """
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.type == kb_type
        ).order_by(
            KnowledgeBase.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """List all knowledge base entries
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of KnowledgeBase instances
        """
        stmt = select(KnowledgeBase).order_by(
            KnowledgeBase.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete(self, kb_id: int) -> bool:
        """Delete a knowledge base entry
        
        Args:
            kb_id: Knowledge base ID
            
        Returns:
            True if deleted, False if not found
        """
        kb = await self.get_by_id(kb_id)
        
        if not kb:
            return False
        
        # Delete file if it's a local file
        if kb.storage_type == 'local' and kb.file_path:
            file_path = Path(kb.file_path)
            file_path.unlink(missing_ok=True)
        
        await self.db.delete(kb)
        await self.db.commit()
        
        logger.info(f"Deleted knowledge base entry: {kb.name} (ID: {kb_id})")
        return True
    
    async def update_content(self, kb_id: int, content: str) -> Optional[KnowledgeBase]:
        """Update knowledge base content (will re-index)
        
        Args:
            kb_id: Knowledge base ID
            content: New content
            
        Returns:
            Updated KnowledgeBase instance or None if not found
        """
        kb = await self.get_by_id(kb_id)
        
        if not kb:
            return None
        
        kb.content = content
        kb.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(kb)
        
        logger.info(f"Updated knowledge base content: {kb.name} (ID: {kb_id})")
        return kb
