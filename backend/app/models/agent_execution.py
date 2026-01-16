"""Agent Execution Model"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AgentExecution(Base):
    """Agent 执行记录
    
    记录每次 Agent 执行的详细信息，用于质量分析和模型对比。
    """
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True)
    execution_id = Column(String(36), unique=True, nullable=False)
    session_id = Column(String(36))
    agent_type = Column(String(50), nullable=False)
    model_name = Column(String(100))
    
    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    
    # Performance metrics
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    duration_ms = Column(Integer)
    token_usage = Column(Integer)
    
    # Quality metrics
    user_accepted = Column(Boolean)
    user_modified = Column(Boolean)
    modification_details = Column(JSON)
    
    # Metadata
    error_message = Column(Text)
    status = Column(String(20), default='completed')
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "agent_type": self.agent_type,
            "model_name": self.model_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "token_usage": self.token_usage,
            "user_accepted": self.user_accepted,
            "user_modified": self.user_modified,
            "modification_details": self.modification_details,
            "error_message": self.error_message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
