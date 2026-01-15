"""Agent Configuration Model"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class AgentConfig(Base):
    """Agent配置表"""
    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False, comment="Agent类型: requirement/scenario/case/code/quality")
    agent_name = Column(String(255), nullable=False, comment="Agent名称")
    model_provider = Column(String(50), nullable=False, comment="模型提供商: openai/anthropic/local")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    prompt_template = Column(Text, nullable=False, comment="提示词模板")
    model_params = Column(JSONB, comment="模型参数: temperature, max_tokens等")
    knowledge_bases = Column(ARRAY(Integer), comment="关联知识库ID数组")
    scripts = Column(ARRAY(Integer), comment="关联脚本ID数组")
    is_default = Column(Boolean, default=False, comment="是否为默认配置")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<AgentConfig(id={self.id}, agent_type={self.agent_type}, agent_name={self.agent_name})>"
