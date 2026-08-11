"""remove org_id and object_id from telemetry_packets

Revision ID: remove_org_object
Revises: b43707249ea3
Create Date: 2026-08-11 13:30:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_org_object'
down_revision: Union[str, Sequence[str], None] = 'b43707249ea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop org_id and object_id columns and their indices."""
    op.drop_index('ix_telemetry_packets_org_id', table_name='telemetry_packets')
    op.drop_index('ix_telemetry_packets_object_id', table_name='telemetry_packets')
    op.drop_column('telemetry_packets', 'org_id')
    op.drop_column('telemetry_packets', 'object_id')


def downgrade() -> None:
    """Restore org_id and object_id columns and their indices."""
    op.add_column('telemetry_packets', sa.Column('object_id', sa.String(length=128), nullable=False))
    op.add_column('telemetry_packets', sa.Column('org_id', sa.String(length=128), nullable=False))
    op.create_index('ix_telemetry_packets_org_id', 'telemetry_packets', ['org_id'], unique=False)
    op.create_index('ix_telemetry_packets_object_id', 'telemetry_packets', ['object_id'], unique=False)
