"""Application Configuration"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/ai_test_case_generator",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )
    
    # LLM API Keys (stored securely, never exposed to frontend)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    
    # Encryption key for sensitive data
    encryption_key: Optional[str] = Field(default=None, alias="ENCRYPTION_KEY")
    
    # LLM API URLs (for custom endpoints or proxies)
    openai_api_base: str = Field(default="https://api.openai.com/v1", alias="OPENAI_API_BASE")
    anthropic_api_base: str = Field(default="https://api.anthropic.com", alias="ANTHROPIC_API_BASE")
    
    # Default LLM Model Configuration
    default_model_provider: str = Field(default="openai", alias="DEFAULT_MODEL_PROVIDER")
    default_model_name: str = Field(default="gpt-4", alias="DEFAULT_MODEL_NAME")
    default_temperature: float = Field(default=0.7, alias="DEFAULT_TEMPERATURE")
    default_max_tokens: int = Field(default=2000, alias="DEFAULT_MAX_TOKENS")
    
    # Agent-specific Model Configuration
    requirement_agent_model: str = Field(default="", alias="REQUIREMENT_AGENT_MODEL")
    scenario_agent_model: str = Field(default="", alias="SCENARIO_AGENT_MODEL")
    case_agent_model: str = Field(default="", alias="CASE_AGENT_MODEL")
    code_agent_model: str = Field(default="", alias="CODE_AGENT_MODEL")
    quality_agent_model: str = Field(default="", alias="QUALITY_AGENT_MODEL")
    optimize_agent_model: str = Field(default="", alias="OPTIMIZE_AGENT_MODEL")
    
    # Application
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_workers: int = Field(default=4, alias="APP_WORKERS")
    
    # Session
    session_expire_hours: int = Field(default=24, alias="SESSION_EXPIRE_HOURS")
    
    # File Upload
    max_upload_size_mb: int = Field(default=10, alias="MAX_UPLOAD_SIZE_MB")
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    
    # Script Execution
    script_timeout_seconds: int = Field(default=30, alias="SCRIPT_TIMEOUT_SECONDS")
    
    # Knowledge Base
    knowledge_base_dir: str = Field(default="./knowledge_base", alias="KNOWLEDGE_BASE_DIR")
    
    # Agent Prompts Directory
    agent_prompts_dir: str = Field(default="./agent_prompts", alias="AGENT_PROMPTS_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", alias="LOG_FILE")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://localhost",
        alias="CORS_ORIGINS"
    )
    
    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @field_validator('openai_api_key', 'anthropic_api_key')
    @classmethod
    def validate_api_keys(cls, v: str) -> str:
        """Validate API keys are not exposed in logs"""
        if v and len(v) > 0:
            # Log masked version only
            masked = f"{v[:3]}...{v[-4:]}" if len(v) > 7 else "***"
            logger.debug(f"API key configured: {masked}")
        return v
    
    def get_masked_openai_key(self) -> str:
        """Get masked OpenAI API key for display"""
        if not self.openai_api_key:
            return "Not configured"
        return f"{self.openai_api_key[:3]}...{self.openai_api_key[-4:]}"
    
    def get_masked_anthropic_key(self) -> str:
        """Get masked Anthropic API key for display"""
        if not self.anthropic_api_key:
            return "Not configured"
        return f"{self.anthropic_api_key[:3]}...{self.anthropic_api_key[-4:]}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
