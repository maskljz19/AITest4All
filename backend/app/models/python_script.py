"""Python Script Model"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.sql import func
from app.core.database import Base


class PythonScript(Base):
    """Python脚本表"""
    __tablename__ = "python_scripts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, comment="脚本名称")
    description = Column(Text, comment="脚本描述")
    code = Column(Text, nullable=False, comment="脚本代码")
    dependencies = Column(ARRAY(String), comment="依赖包列表")
    is_builtin = Column(Boolean, default=False, comment="是否为内置脚本")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<PythonScript(id={self.id}, name={self.name})>"
