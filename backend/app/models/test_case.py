"""Test Case Model (Optional)"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class TestCase(Base):
    """测试用例表 (可选)"""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), nullable=False, comment="用例ID")
    session_id = Column(String(100), index=True, comment="会话ID")
    title = Column(String(500), nullable=False, comment="用例标题")
    test_type = Column(String(50), nullable=False, comment="测试类型: ui/api/unit")
    priority = Column(String(10), nullable=False, comment="优先级: P0/P1/P2/P3")
    precondition = Column(Text, comment="前置条件")
    steps = Column(JSONB, nullable=False, comment="测试步骤")
    test_data = Column(JSONB, comment="测试数据")
    expected_result = Column(Text, comment="预期结果")
    postcondition = Column(Text, comment="后置条件")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<TestCase(id={self.id}, case_id={self.case_id}, title={self.title})>"


# Create index on session_id
Index('idx_test_cases_session', TestCase.session_id)
