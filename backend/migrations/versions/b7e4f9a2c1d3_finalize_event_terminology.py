"""finalize event terminology: event_id, event_type, source

Revision ID: b7e4f9a2c1d3
Revises: ee00c3dfb27a
Create Date: 2026-10-23 13:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers for Alembic.
revision: str = 'b7e4f9a2c1d3'
down_revision: Union[str, Sequence[str], None] = 'ee00c3dfb27a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE skinsense.event_log_details DROP CONSTRAINT IF EXISTS event_log_details_job_id_fkey')
    op.execute('DROP INDEX IF EXISTS skinsense.idx_event_log_job_id')
    op.alter_column('event_log_details', 'job_id', new_column_name='event_id', existing_type=sa.String(), schema='skinsense')
    op.add_column('event_log_details', sa.Column('event_type', sa.String(), nullable=True), schema='skinsense')
    op.add_column('event_log_details', sa.Column('source', sa.String(), nullable=False, server_default='scheduled'), schema='skinsense')
    op.drop_column('event_log_details', 'action', schema='skinsense')
    op.create_index('idx_event_log_event_id', 'event_log_details', ['event_id'], schema='skinsense')
    op.alter_column('job_log_details', 'event_name', new_column_name='event_type', existing_type=sa.String(), schema='skinsense')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('job_log_details', 'event_type', new_column_name='event_name', existing_type=sa.String(), schema='skinsense')
    op.drop_index('idx_event_log_event_id', table_name='event_log_details', schema='skinsense')
    op.add_column('event_log_details', sa.Column('action', sa.String(), nullable=True), schema='skinsense')
    op.drop_column('event_log_details', 'source', schema='skinsense')
    op.drop_column('event_log_details', 'event_type', schema='skinsense')
    op.alter_column('event_log_details', 'event_id', new_column_name='job_id', existing_type=sa.String(), schema='skinsense')
    op.create_index('idx_event_log_job_id', 'event_log_details', ['job_id'], schema='skinsense')
    op.create_foreign_key('event_log_details_job_id_fkey', 'event_log_details', 'job_log_details', ['job_id'], ['job_id'], source_schema='skinsense', referent_schema='skinsense')
