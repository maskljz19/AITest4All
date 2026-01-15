"""Application Configuration"""

from pydantic_settings import BaseSettings
from pydantic import Field


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
    
    # LLM API Keys
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    
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
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", alias="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
