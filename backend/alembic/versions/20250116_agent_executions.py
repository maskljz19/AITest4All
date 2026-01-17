"""Add agent_executions table

Revision ID: 20250116_agent_executions
Revises: 20250115_seed_data
Create Date: 2025-01-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250116_agent_executions'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create agent_executions table
    op.create_table(
        'agent_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('execution_id', sa.String(36), nullable=False),
        sa.Column('session_id', sa.String(36), nullable=True),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=True),
        
        # Input/Output
        sa.Column('input_data', postgresql.JSONB(), nullable=True),
        sa.Column('output_data', postgresql.JSONB(), nullable=True),
        
        # Performance metrics
        sa.Column('start_time', sa.TIMESTAMP(), nullable=False),
        sa.Column('end_time', sa.TIMESTAMP(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('token_usage', sa.Integer(), nullable=True),
        
        # Quality metrics
        sa.Column('user_accepted', sa.Boolean(), nullable=True),
        sa.Column('user_modified', sa.Boolean(), nullable=True),
        sa.Column('modification_details', postgresql.JSONB(), nullable=True),
        
        # Metadata
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default='completed', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('execution_id')
    )
    
    # Create indexes
    op.create_index('idx_agent_executions_session', 'agent_executions', ['session_id'])
    op.create_index('idx_agent_executions_agent_type', 'agent_executions', ['agent_type'])
    op.create_index('idx_agent_executions_created_at', 'agent_executions', ['created_at'])
    op.create_index('idx_agent_executions_status', 'agent_executions', ['status'])


def downgrade():
    op.drop_index('idx_agent_executions_status', table_name='agent_executions')
    op.drop_index('idx_agent_executions_created_at', table_name='agent_executions')
    op.drop_index('idx_agent_executions_agent_type', table_name='agent_executions')
    op.drop_index('idx_agent_executions_session', table_name='agent_executions')
    op.drop_table('agent_executions')
