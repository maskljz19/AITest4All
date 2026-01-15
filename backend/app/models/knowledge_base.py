"""Knowledge Base Model"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.sql import func
from app.core.database import Base


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="知识库名称")
    type = Column(String(50), nullable=False, index=True, comment="类型: case/defect/rule/api")
    storage_type = Column(String(50), nullable=False, comment="存储类型: local/url/database")
    file_path = Column(Text, comment="本地文件路径")
    url = Column(Text, comment="外部URL")
    content = Column(Text, comment="文档内容")
    meta_data = Column("metadata", JSONB, comment="元数据")
    search_vector = Column(TSVECTOR, comment="全文搜索向量")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name}, type={self.type})>"


# Create indexes
Index('idx_knowledge_search', KnowledgeBase.search_vector, postgresql_using='gin')
