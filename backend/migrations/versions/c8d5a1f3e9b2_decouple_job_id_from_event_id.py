"""decouple job_id from event_id; add action/event_id to job_log_details

Revision ID: c8d5a1f3e9b2
Revises: b7e4f9a2c1d3
Create Date: 2026-10-23 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers for Alembic.
revision: str = 'c8d5a1f3e9b2'
down_revision: Union[str, Sequence[str], None] = 'b7e4f9a2c1d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE skinsense.job_log_details DROP CONSTRAINT IF EXISTS job_log_details_job_id_key')
    op.add_column('job_log_details', sa.Column('event_id', sa.String(), nullable=True), schema='skinsense')
    op.execute('UPDATE skinsense.job_log_details SET event_id = job_id')
    op.add_column('job_log_details', sa.Column('action', sa.String(), nullable=True), schema='skinsense')
    op.execute('UPDATE skinsense.job_log_details SET action = status')
    op.execute("UPDATE skinsense.job_log_details SET action = REPLACE(action, ' - Failed', '')")
    op.execute("UPDATE skinsense.job_log_details SET status = CASE WHEN job_end_time IS NULL THEN 'Running' WHEN status LIKE '% - Failed' THEN 'Failed' ELSE 'Success' END")
    op.drop_column('job_log_details', 'event_type', schema='skinsense')
    op.alter_column('job_log_details', 'event_id', existing_type=sa.String(), nullable=False, schema='skinsense')
    op.alter_column('job_log_details', 'action', existing_type=sa.String(), nullable=False, schema='skinsense')
    op.create_index('idx_job_log_event_id', 'job_log_details', ['event_id'], schema='skinsense')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_job_log_event_id', table_name='job_log_details', schema='skinsense')
    op.add_column('job_log_details', sa.Column('event_type', sa.String(), nullable=True), schema='skinsense')
    op.execute("UPDATE skinsense.job_log_details SET status = CASE WHEN status = 'Failed' THEN action || ' - Failed' ELSE action END")
    op.drop_column('job_log_details', 'action', schema='skinsense')
    op.drop_column('job_log_details', 'event_id', schema='skinsense')
    op.create_unique_constraint('job_log_details_job_id_key', 'job_log_details', ['job_id'], schema='skinsense')
