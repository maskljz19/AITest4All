"""Session Manager Service

Manages user generation sessions using Redis for temporary storage.
Sessions expire after 24 hours by default.
"""

import json
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionError(Exception):
    """Exception raised for session operations"""
    pass


class SessionManager:
    """Service for managing user generation sessions"""
    
    # Session key prefixes
    KEY_PREFIX = "session"
    METADATA_SUFFIX = "metadata"
    
    # Session steps
    STEP_REQUIREMENT_ANALYSIS = "requirement_analysis"
    STEP_SCENARIOS = "scenarios"
    STEP_CASES = "cases"
    STEP_CODE = "code"
    STEP_QUALITY_REPORT = "quality_report"
    STEP_CONVERSATION = "conversation"
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.expire_seconds = settings.session_expire_hours * 3600
    
    def _make_key(self, session_id: str, step: Optional[str] = None) -> str:
        """Generate Redis key for session data
        
        Args:
            session_id: Session ID
            step: Optional step name
            
        Returns:
            Redis key string
        """
        if step:
            return f"{self.KEY_PREFIX}:{session_id}:{step}"
        return f"{self.KEY_PREFIX}:{session_id}"
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Generated session ID
        """
        session_id = str(uuid.uuid4())
        
        # Initialize session metadata
        metadata = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat(),
            'current_step': None,
            'steps_completed': []
        }
        
        await self.save_metadata(session_id, metadata)
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    async def save_step_result(
        self,
        session_id: str,
        step: str,
        data: Dict[str, Any]
    ) -> None:
        """Save step result to session
        
        Args:
            session_id: Session ID
            step: Step name
            data: Step result data
            
        Raises:
            SessionError: If save fails
        """
        try:
            key = self._make_key(session_id, step)
            
            # Serialize data to JSON
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Save to Redis with expiration
            await self.redis.setex(
                key,
                self.expire_seconds,
                json_data
            )
            
            # Update metadata
            metadata = await self.get_metadata(session_id)
            if metadata:
                metadata['current_step'] = step
                metadata['last_accessed'] = datetime.utcnow().isoformat()
                
                if step not in metadata.get('steps_completed', []):
                    metadata.setdefault('steps_completed', []).append(step)
                
                await self.save_metadata(session_id, metadata)
            
            logger.debug(f"Saved step result: {session_id}:{step}")
            
        except Exception as e:
            logger.error(f"Failed to save step result: {str(e)}")
            raise SessionError(f"Failed to save step result: {str(e)}")
    
    async def get_step_result(
        self,
        session_id: str,
        step: str
    ) -> Optional[Dict[str, Any]]:
        """Get step result from session
        
        Args:
            session_id: Session ID
            step: Step name
            
        Returns:
            Step result data or None if not found
        """
        try:
            key = self._make_key(session_id, step)
            
            # Get from Redis
            json_data = await self.redis.get(key)
            
            if json_data is None:
                return None
            
            # Deserialize JSON
            data = json.loads(json_data)
            
            # Update last accessed time
            metadata = await self.get_metadata(session_id)
            if metadata:
                metadata['last_accessed'] = datetime.utcnow().isoformat()
                await self.save_metadata(session_id, metadata)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get step result: {str(e)}")
            return None
    
    async def save_metadata(
        self,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Save session metadata
        
        Args:
            session_id: Session ID
            metadata: Metadata dictionary
        """
        try:
            key = self._make_key(session_id, self.METADATA_SUFFIX)
            json_data = json.dumps(metadata, ensure_ascii=False)
            
            await self.redis.setex(
                key,
                self.expire_seconds,
                json_data
            )
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
            raise SessionError(f"Failed to save metadata: {str(e)}")
    
    async def get_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata
        
        Args:
            session_id: Session ID
            
        Returns:
            Metadata dictionary or None if not found
        """
        try:
            key = self._make_key(session_id, self.METADATA_SUFFIX)
            json_data = await self.redis.get(key)
            
            if json_data is None:
                return None
            
            return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Failed to get metadata: {str(e)}")
            return None
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session exists, False otherwise
        """
        key = self._make_key(session_id, self.METADATA_SUFFIX)
        return await self.redis.exists(key) > 0
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its data
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get all keys for this session
            pattern = self._make_key(session_id, "*")
            keys = []
            
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if not keys:
                return False
            
            # Delete all keys
            await self.redis.delete(*keys)
            
            logger.info(f"Deleted session: {session_id} ({len(keys)} keys)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            raise SessionError(f"Failed to delete session: {str(e)}")
    
    async def extend_session(self, session_id: str) -> bool:
        """Extend session expiration time
        
        Args:
            session_id: Session ID
            
        Returns:
            True if extended, False if session not found
        """
        try:
            # Get all keys for this session
            pattern = self._make_key(session_id, "*")
            keys = []
            
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if not keys:
                return False
            
            # Extend expiration for all keys
            for key in keys:
                await self.redis.expire(key, self.expire_seconds)
            
            logger.debug(f"Extended session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extend session: {str(e)}")
            return False
    
    async def get_all_steps(self, session_id: str) -> Dict[str, Any]:
        """Get all step results for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with all step results
        """
        steps = [
            self.STEP_REQUIREMENT_ANALYSIS,
            self.STEP_SCENARIOS,
            self.STEP_CASES,
            self.STEP_CODE,
            self.STEP_QUALITY_REPORT,
            self.STEP_CONVERSATION
        ]
        
        results = {}
        
        for step in steps:
            data = await self.get_step_result(session_id, step)
            if data is not None:
                results[step] = data
        
        return results
    
    async def clear_step(self, session_id: str, step: str) -> bool:
        """Clear a specific step result
        
        Args:
            session_id: Session ID
            step: Step name
            
        Returns:
            True if cleared, False if not found
        """
        try:
            key = self._make_key(session_id, step)
            deleted = await self.redis.delete(key)
            
            # Update metadata
            if deleted > 0:
                metadata = await self.get_metadata(session_id)
                if metadata and step in metadata.get('steps_completed', []):
                    metadata['steps_completed'].remove(step)
                    await self.save_metadata(session_id, metadata)
            
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Failed to clear step: {str(e)}")
            return False
    
    async def add_conversation_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """Add a message to conversation history
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant/system)
            content: Message content
        """
        # Get existing conversation
        conversation = await self.get_step_result(session_id, self.STEP_CONVERSATION)
        
        if conversation is None:
            conversation = {'messages': []}
        
        # Add new message
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        conversation['messages'].append(message)
        
        # Save updated conversation
        await self.save_step_result(session_id, self.STEP_CONVERSATION, conversation)
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history
        
        Args:
            session_id: Session ID
            limit: Optional limit on number of messages
            
        Returns:
            List of conversation messages
        """
        conversation = await self.get_step_result(session_id, self.STEP_CONVERSATION)
        
        if conversation is None:
            return []
        
        messages = conversation.get('messages', [])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
