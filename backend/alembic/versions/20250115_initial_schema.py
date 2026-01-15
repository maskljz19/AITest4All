"""initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agent_configs table
    op.create_table(
        'agent_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False, comment='Agent类型: requirement/scenario/case/code/quality'),
        sa.Column('agent_name', sa.String(length=255), nullable=False, comment='Agent名称'),
        sa.Column('model_provider', sa.String(length=50), nullable=False, comment='模型提供商: openai/anthropic/local'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('prompt_template', sa.Text(), nullable=False, comment='提示词模板'),
        sa.Column('model_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='模型参数: temperature, max_tokens等'),
        sa.Column('knowledge_bases', postgresql.ARRAY(sa.Integer()), nullable=True, comment='关联知识库ID数组'),
        sa.Column('scripts', postgresql.ARRAY(sa.Integer()), nullable=True, comment='关联脚本ID数组'),
        sa.Column('is_default', sa.Boolean(), nullable=True, comment='是否为默认配置'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_configs_id'), 'agent_configs', ['id'], unique=False)

    # Create knowledge_bases table
    op.create_table(
        'knowledge_bases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='知识库名称'),
        sa.Column('type', sa.String(length=50), nullable=False, comment='类型: case/defect/rule/api'),
        sa.Column('storage_type', sa.String(length=50), nullable=False, comment='存储类型: local/url/database'),
        sa.Column('file_path', sa.Text(), nullable=True, comment='本地文件路径'),
        sa.Column('url', sa.Text(), nullable=True, comment='外部URL'),
        sa.Column('content', sa.Text(), nullable=True, comment='文档内容'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='元数据'),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True, comment='全文搜索向量'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_bases_id'), 'knowledge_bases', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_bases_type'), 'knowledge_bases', ['type'], unique=False)
    op.create_index('idx_knowledge_search', 'knowledge_bases', ['search_vector'], unique=False, postgresql_using='gin')

    # Create trigger for automatic search_vector update
    op.execute("""
        CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE
        ON knowledge_bases FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.simple', content);
    """)

    # Create python_scripts table
    op.create_table(
        'python_scripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='脚本名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='脚本描述'),
        sa.Column('code', sa.Text(), nullable=False, comment='脚本代码'),
        sa.Column('dependencies', postgresql.ARRAY(sa.String()), nullable=True, comment='依赖包列表'),
        sa.Column('is_builtin', sa.Boolean(), nullable=True, comment='是否为内置脚本'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_python_scripts_id'), 'python_scripts', ['id'], unique=False)

    # Create case_templates table
    op.create_table(
        'case_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='模板名称'),
        sa.Column('test_type', sa.String(length=50), nullable=False, comment='测试类型: ui/api/unit'),
        sa.Column('template_structure', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='模板结构'),
        sa.Column('is_builtin', sa.Boolean(), nullable=True, comment='是否为内置模板'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_templates_id'), 'case_templates', ['id'], unique=False)

    # Create test_cases table (optional)
    op.create_table(
        'test_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False, comment='用例ID'),
        sa.Column('session_id', sa.String(length=100), nullable=True, comment='会话ID'),
        sa.Column('title', sa.String(length=500), nullable=False, comment='用例标题'),
        sa.Column('test_type', sa.String(length=50), nullable=False, comment='测试类型: ui/api/unit'),
        sa.Column('priority', sa.String(length=10), nullable=False, comment='优先级: P0/P1/P2/P3'),
        sa.Column('precondition', sa.Text(), nullable=True, comment='前置条件'),
        sa.Column('steps', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='测试步骤'),
        sa.Column('test_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='测试数据'),
        sa.Column('expected_result', sa.Text(), nullable=True, comment='预期结果'),
        sa.Column('postcondition', sa.Text(), nullable=True, comment='后置条件'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_cases_id'), 'test_cases', ['id'], unique=False)
    op.create_index('idx_test_cases_session', 'test_cases', ['session_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_test_cases_session', table_name='test_cases')
    op.drop_index(op.f('ix_test_cases_id'), table_name='test_cases')
    op.drop_table('test_cases')
    
    op.drop_index(op.f('ix_case_templates_id'), table_name='case_templates')
    op.drop_table('case_templates')
    
    op.drop_index(op.f('ix_python_scripts_id'), table_name='python_scripts')
    op.drop_table('python_scripts')
    
    # Drop trigger before dropping table
    op.execute("DROP TRIGGER IF EXISTS tsvector_update ON knowledge_bases;")
    op.drop_index('idx_knowledge_search', table_name='knowledge_bases')
    op.drop_index(op.f('ix_knowledge_bases_type'), table_name='knowledge_bases')
    op.drop_index(op.f('ix_knowledge_bases_id'), table_name='knowledge_bases')
    op.drop_table('knowledge_bases')
    
    op.drop_index(op.f('ix_agent_configs_id'), table_name='agent_configs')
    op.drop_table('agent_configs')
