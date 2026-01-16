"""Base Agent Framework"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

import openai
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.prompt_manager import prompt_manager


class ModelProvider(str, Enum):
    """LLM Model Provider"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class BaseAgent(ABC):
    """
    Base Agent class for all AI agents.
    
    Provides:
    - LLM API integration (OpenAI/Anthropic)
    - Streaming output support
    - Automatic retry with exponential backoff
    - Error handling
    - Tool integration
    - Execution tracking
    """
    
    def __init__(
        self,
        agent_type: str,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3,
        tools: Optional[List[Any]] = None,
        fallback_model: Optional[str] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_type: Type of agent (requirement/scenario/case/code/quality)
            model_provider: LLM provider (openai/anthropic/local)
            model_name: Model name (e.g., gpt-4, claude-3-opus)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum retry attempts on failure
            tools: List of tools available to this agent
            fallback_model: Optional fallback model name (e.g., gpt-3.5-turbo)
        """
        self.agent_type = agent_type
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.fallback_model = fallback_model
        
        # Tool integration
        self.tools = {tool.name: tool for tool in (tools or [])}
        
        # Load system prompt from configuration
        self.system_prompt = prompt_manager.get_prompt(f"{agent_type}_agent")
        
        # Initialize LLM clients
        self._init_llm_clients()
    
    def _init_llm_clients(self):
        """Initialize LLM API clients"""
        if self.model_provider == ModelProvider.OPENAI:
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.openai_client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base
            )
        elif self.model_provider == ModelProvider.ANTHROPIC:
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            self.anthropic_client = AsyncAnthropic(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_api_base
            )
        elif self.model_provider == ModelProvider.LOCAL:
            # TODO: Implement local model support
            raise NotImplementedError("Local model support not yet implemented")
    
    def get_tool(self, tool_name: str):
        """Get tool by name
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool instance or None
        """
        return self.tools.get(tool_name)
    
    @abstractmethod
    def build_prompt(self, **kwargs) -> str:
        """
        Build prompt for the agent.
        
        Must be implemented by subclasses.
        
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured data.
        
        Must be implemented by subclasses.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed structured data
        """
        pass
    
    async def _call_openai(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """
        Call OpenAI API.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            stream: Whether to stream response
            
        Returns:
            Response text or async generator for streaming
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        if stream:
            # Streaming response
            async def stream_generator():
                response = await self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True
                )
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            return stream_generator()
        else:
            # Non-streaming response
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )
            return response.choices[0].message.content
    
    async def _call_anthropic(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """
        Call Anthropic API.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            stream: Whether to stream response
            
        Returns:
            Response text or async generator for streaming
        """
        kwargs = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        if stream:
            # Streaming response
            async def stream_generator():
                async with self.anthropic_client.messages.stream(**kwargs) as stream:
                    async for text in stream.text_stream:
                        yield text
            
            return stream_generator()
        else:
            # Non-streaming response
            response = await self.anthropic_client.messages.create(**kwargs)
            return response.content[0].text
    
    async def _call_llm_with_retry(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        stream: bool = False,
        timeout: Optional[int] = None
    ) -> AsyncGenerator[str, None] | str:
        """
        Call LLM with automatic retry and exponential backoff.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            stream: Whether to stream response
            timeout: Optional timeout in seconds (default: 60s)
            
        Returns:
            Response text or async generator for streaming
            
        Raises:
            LLMAPIError: If all retries fail
        """
        from app.core.exceptions import LLMAPIError, TimeoutError as AppTimeoutError
        
        timeout = timeout or 60  # Default 60 seconds
        last_error = None
        original_model = self.model_name
        
        for attempt in range(self.max_retries):
            try:
                # Wrap LLM call with timeout
                if self.model_provider == ModelProvider.OPENAI:
                    result = await asyncio.wait_for(
                        self._call_openai(prompt, system_message, stream),
                        timeout=timeout
                    )
                elif self.model_provider == ModelProvider.ANTHROPIC:
                    result = await asyncio.wait_for(
                        self._call_anthropic(prompt, system_message, stream),
                        timeout=timeout
                    )
                else:
                    raise NotImplementedError(f"Provider {self.model_provider} not supported")
                
                # Success - restore original model if we used fallback
                if self.model_name != original_model:
                    self.model_name = original_model
                
                return result
            
            except asyncio.TimeoutError as e:
                last_error = e
                error_msg = f"LLM API call timed out after {timeout}s (attempt {attempt + 1}/{self.max_retries})"
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    import logging
                    logging.warning(f"{error_msg}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Try fallback model if available
                    if self.fallback_model and self.model_name != self.fallback_model:
                        import logging
                        logging.warning(f"Primary model failed. Trying fallback model: {self.fallback_model}")
                        self.model_name = self.fallback_model
                        try:
                            result = await self._call_llm_with_retry(prompt, system_message, stream, timeout)
                            self.model_name = original_model
                            return result
                        except Exception as fallback_error:
                            self.model_name = original_model
                            raise LLMAPIError(
                                message=f"Both primary and fallback models failed",
                                details={
                                    "primary_model": original_model,
                                    "fallback_model": self.fallback_model,
                                    "primary_error": str(last_error),
                                    "fallback_error": str(fallback_error)
                                }
                            )
                    
                    # All retries exhausted
                    raise AppTimeoutError(
                        message=f"LLM API call timed out after {self.max_retries} attempts",
                        details={
                            "timeout": timeout,
                            "attempts": self.max_retries,
                            "provider": self.model_provider,
                            "model": original_model
                        }
                    )
            
            except (openai.APIError, openai.APIConnectionError, openai.RateLimitError) as e:
                last_error = e
                error_msg = f"OpenAI API error: {str(e)} (attempt {attempt + 1}/{self.max_retries})"
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    import logging
                    logging.warning(f"{error_msg}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Try fallback model if available
                    if self.fallback_model and self.model_name != self.fallback_model:
                        import logging
                        logging.warning(f"Primary model failed. Trying fallback model: {self.fallback_model}")
                        self.model_name = self.fallback_model
                        try:
                            result = await self._call_llm_with_retry(prompt, system_message, stream, timeout)
                            self.model_name = original_model
                            return result
                        except Exception as fallback_error:
                            self.model_name = original_model
                            raise LLMAPIError(
                                message=f"Both primary and fallback models failed",
                                details={
                                    "primary_model": original_model,
                                    "fallback_model": self.fallback_model,
                                    "primary_error": str(last_error),
                                    "fallback_error": str(fallback_error)
                                }
                            )
                    
                    # All retries exhausted
                    raise LLMAPIError(
                        message=f"OpenAI API call failed after {self.max_retries} attempts: {str(e)}",
                        details={
                            "error_type": type(e).__name__,
                            "attempts": self.max_retries,
                            "provider": self.model_provider,
                            "model": original_model
                        }
                    )
            
            except Exception as e:
                last_error = e
                error_msg = f"LLM API error: {str(e)} (attempt {attempt + 1}/{self.max_retries})"
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    import logging
                    logging.warning(f"{error_msg}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Try fallback model if available
                    if self.fallback_model and self.model_name != self.fallback_model:
                        import logging
                        logging.warning(f"Primary model failed. Trying fallback model: {self.fallback_model}")
                        self.model_name = self.fallback_model
                        try:
                            result = await self._call_llm_with_retry(prompt, system_message, stream, timeout)
                            self.model_name = original_model
                            return result
                        except Exception as fallback_error:
                            self.model_name = original_model
                            raise LLMAPIError(
                                message=f"Both primary and fallback models failed",
                                details={
                                    "primary_model": original_model,
                                    "fallback_model": self.fallback_model,
                                    "primary_error": str(last_error),
                                    "fallback_error": str(fallback_error)
                                }
                            )
                    
                    # All retries exhausted
                    raise LLMAPIError(
                        message=f"LLM API call failed after {self.max_retries} attempts: {str(e)}",
                        details={
                            "error_type": type(e).__name__,
                            "attempts": self.max_retries,
                            "provider": self.model_provider,
                            "model": original_model
                        }
                    )
    
    async def _create_execution_record(self, session_id: Optional[str], input_data: Dict[str, Any]):
        """Create execution record
        
        Args:
            session_id: Session ID
            input_data: Input data
            
        Returns:
            Execution record dict
        """
        return {
            "execution_id": str(uuid.uuid4()),
            "session_id": session_id,
            "agent_type": self.agent_type,
            "model_name": self.model_name,
            "input_data": input_data,
            "start_time": datetime.utcnow(),
            "status": "running"
        }
    
    async def _save_execution_record(self, execution_record: Dict[str, Any]):
        """Save execution record to database
        
        Args:
            execution_record: Execution record
        """
        try:
            from app.core.database import get_async_session
            from app.models.agent_execution import AgentExecution
            
            async with get_async_session() as db:
                # Calculate duration
                if execution_record.get("end_time") and execution_record.get("start_time"):
                    duration = (execution_record["end_time"] - execution_record["start_time"]).total_seconds() * 1000
                    execution_record["duration_ms"] = int(duration)
                
                # Create model instance
                execution = AgentExecution(**execution_record)
                db.add(execution)
                await db.commit()
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logging.error(f"Failed to save execution record: {e}")
    
    async def generate(
        self,
        stream: bool = False,
        system_message: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any] | AsyncGenerator[str, None]:
        """
        Generate response from agent with execution tracking.
        
        Args:
            stream: Whether to stream response
            system_message: Optional system message (overrides default prompt)
            session_id: Optional session ID for tracking
            **kwargs: Arguments for building prompt
            
        Returns:
            Parsed response dict or async generator for streaming
        """
        # Create execution record
        execution_record = await self._create_execution_record(session_id, kwargs)
        
        try:
            # Use provided system message or default prompt
            sys_msg = system_message or self.system_prompt
            
            # Build prompt
            prompt = self.build_prompt(**kwargs)
            
            if stream:
                # Return streaming generator
                async def stream_and_parse():
                    full_response = ""
                    async for chunk in await self._call_llm_with_retry(
                        prompt, sys_msg, stream=True
                    ):
                        full_response += chunk
                        yield chunk
                    
                    # Store full response for potential parsing
                    self._last_response = full_response
                    
                    # Update execution record
                    execution_record["end_time"] = datetime.utcnow()
                    execution_record["status"] = "completed"
                    execution_record["output_data"] = {"response": full_response}
                    await self._save_execution_record(execution_record)
                
                return stream_and_parse()
            else:
                # Get full response and parse
                response = await self._call_llm_with_retry(prompt, sys_msg, stream=False)
                parsed_result = self.parse_response(response)
                
                # Update execution record
                execution_record["end_time"] = datetime.utcnow()
                execution_record["status"] = "completed"
                execution_record["output_data"] = parsed_result
                await self._save_execution_record(execution_record)
                
                return parsed_result
                
        except Exception as e:
            # Update execution record with error
            execution_record["end_time"] = datetime.utcnow()
            execution_record["status"] = "failed"
            execution_record["error_message"] = str(e)
            await self._save_execution_record(execution_record)
            raise
    
    async def generate_streaming(
        self,
        system_message: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming response with structured chunks.
        
        Yields:
            Dict with 'type' and 'content' keys
        """
        # Create execution record
        execution_record = await self._create_execution_record(session_id, kwargs)
        
        try:
            # Use provided system message or default prompt
            sys_msg = system_message or self.system_prompt
            
            prompt = self.build_prompt(**kwargs)
            full_response = ""
            
            async for chunk in await self._call_llm_with_retry(
                prompt, sys_msg, stream=True
            ):
                full_response += chunk
                yield {
                    "type": "chunk",
                    "content": chunk,
                    "metadata": {
                        "agent": self.agent_type,
                        "model": self.model_name,
                        "execution_id": execution_record["execution_id"]
                    }
                }
            
            # Parse final response
            try:
                parsed = self.parse_response(full_response)
                
                # Update execution record
                execution_record["end_time"] = datetime.utcnow()
                execution_record["status"] = "completed"
                execution_record["output_data"] = parsed
                await self._save_execution_record(execution_record)
                
                yield {
                    "type": "done",
                    "content": parsed,
                    "metadata": {
                        "agent": self.agent_type,
                        "model": self.model_name,
                        "execution_id": execution_record["execution_id"]
                    }
                }
            except Exception as e:
                # Update execution record with parse error
                execution_record["end_time"] = datetime.utcnow()
                execution_record["status"] = "failed"
                execution_record["error_message"] = f"Parse error: {str(e)}"
                await self._save_execution_record(execution_record)
                
                yield {
                    "type": "error",
                    "error": f"Failed to parse response: {str(e)}",
                    "metadata": {
                        "agent": self.agent_type,
                        "model": self.model_name,
                        "execution_id": execution_record["execution_id"]
                    }
                }
        
        except Exception as e:
            # Update execution record with error
            execution_record["end_time"] = datetime.utcnow()
            execution_record["status"] = "failed"
            execution_record["error_message"] = str(e)
            await self._save_execution_record(execution_record)
            
            yield {
                "type": "error",
                "error": str(e),
                "metadata": {
                    "agent": self.agent_type,
                    "model": self.model_name,
                    "execution_id": execution_record["execution_id"]
                }
            }

