"""add example_input to python_scripts

Revision ID: 20250117_add_example_input
Revises: 20250116_agent_executions
Create Date: 2025-01-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250117_add_example_input'
down_revision = '20250116_agent_executions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add example_input column to python_scripts table"""
    op.add_column(
        'python_scripts',
        sa.Column('example_input', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='示例输入参数')
    )


def downgrade() -> None:
    """Remove example_input column from python_scripts table"""
    op.drop_column('python_scripts', 'example_input')
