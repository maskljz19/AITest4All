"""Case Template Model"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class CaseTemplate(Base):
    """用例模板表"""
    __tablename__ = "case_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="模板名称")
    test_type = Column(String(50), nullable=False, comment="测试类型: ui/api/unit")
    template_structure = Column(JSONB, nullable=False, comment="模板结构")
    is_builtin = Column(Boolean, default=False, comment="是否为内置模板")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<CaseTemplate(id={self.id}, name={self.name}, test_type={self.test_type})>"
