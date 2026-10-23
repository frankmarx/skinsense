"""rename job_start_time/job_end_time to start_time/end_time

Revision ID: e3f8c5a7d1b9
Revises: d9e6b2c4f8a1
Create Date: 2026-10-23 17:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers for Alembic.
revision: str = 'e3f8c5a7d1b9'
down_revision: Union[str, Sequence[str], None] = 'd9e6b2c4f8a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('job_log_details', 'job_start_time', new_column_name='start_time', existing_type=sa.DateTime(), schema='skinsense')
    op.alter_column('job_log_details', 'job_end_time', new_column_name='end_time', existing_type=sa.DateTime(), schema='skinsense')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('job_log_details', 'end_time', new_column_name='job_end_time', existing_type=sa.DateTime(), schema='skinsense')
    op.alter_column('job_log_details', 'start_time', new_column_name='job_start_time', existing_type=sa.DateTime(), schema='skinsense')
