"""Base Agent Framework"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any, List
from enum import Enum

import openai
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import settings


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
    """
    
    def __init__(
        self,
        agent_type: str,
        model_provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3
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
        """
        self.agent_type = agent_type
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        
        # Initialize LLM clients
        self._init_llm_clients()
    
    def _init_llm_clients(self):
        """Initialize LLM API clients"""
        if self.model_provider == ModelProvider.OPENAI:
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.model_provider == ModelProvider.ANTHROPIC:
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        elif self.model_provider == ModelProvider.LOCAL:
            # TODO: Implement local model support
            raise NotImplementedError("Local model support not yet implemented")
    
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
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """
        Call LLM with automatic retry and exponential backoff.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            stream: Whether to stream response
            
        Returns:
            Response text or async generator for streaming
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if self.model_provider == ModelProvider.OPENAI:
                    return await self._call_openai(prompt, system_message, stream)
                elif self.model_provider == ModelProvider.ANTHROPIC:
                    return await self._call_anthropic(prompt, system_message, stream)
                else:
                    raise NotImplementedError(f"Provider {self.model_provider} not supported")
            
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # All retries exhausted
                    raise Exception(
                        f"LLM API call failed after {self.max_retries} attempts: {str(last_error)}"
                    )
    
    async def generate(
        self,
        stream: bool = False,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any] | AsyncGenerator[str, None]:
        """
        Generate response from agent.
        
        Args:
            stream: Whether to stream response
            system_message: Optional system message
            **kwargs: Arguments for building prompt
            
        Returns:
            Parsed response dict or async generator for streaming
        """
        # Build prompt
        prompt = self.build_prompt(**kwargs)
        
        if stream:
            # Return streaming generator
            async def stream_and_parse():
                full_response = ""
                async for chunk in await self._call_llm_with_retry(
                    prompt, system_message, stream=True
                ):
                    full_response += chunk
                    yield chunk
                
                # Store full response for potential parsing
                self._last_response = full_response
            
            return stream_and_parse()
        else:
            # Get full response and parse
            response = await self._call_llm_with_retry(prompt, system_message, stream=False)
            return self.parse_response(response)
    
    async def generate_streaming(
        self,
        system_message: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming response with structured chunks.
        
        Yields:
            Dict with 'type' and 'content' keys
        """
        try:
            prompt = self.build_prompt(**kwargs)
            full_response = ""
            
            async for chunk in await self._call_llm_with_retry(
                prompt, system_message, stream=True
            ):
                full_response += chunk
                yield {
                    "type": "chunk",
                    "content": chunk,
                    "metadata": {
                        "agent": self.agent_type,
                        "model": self.model_name
                    }
                }
            
            # Parse final response
            try:
                parsed = self.parse_response(full_response)
                yield {
                    "type": "done",
                    "content": parsed,
                    "metadata": {
                        "agent": self.agent_type,
                        "model": self.model_name
                    }
                }
            except Exception as e:
                yield {
                    "type": "error",
                    "error": f"Failed to parse response: {str(e)}",
                    "metadata": {
                        "agent": self.agent_type,
                        "model": self.model_name
                    }
                }
        
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "metadata": {
                    "agent": self.agent_type,
                    "model": self.model_name
                }
            }
