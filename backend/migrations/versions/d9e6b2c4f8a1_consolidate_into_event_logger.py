"""consolidate logging into EventLogger; single-row jobs with Completed status

Revision ID: d9e6b2c4f8a1
Revises: c8d5a1f3e9b2
Create Date: 2026-10-23 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers for Alembic.
revision: str = 'd9e6b2c4f8a1'
down_revision: Union[str, Sequence[str], None] = 'c8d5a1f3e9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE skinsense.job_log_details SET status = 'Completed' WHERE status = 'Success'")
    op.drop_column('job_log_details', 'data_source_id', schema='skinsense')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('job_log_details', sa.Column('data_source_id', sa.String(), nullable=True), schema='skinsense')
    op.execute("UPDATE skinsense.job_log_details SET status = 'Success' WHERE status = 'Completed'")
