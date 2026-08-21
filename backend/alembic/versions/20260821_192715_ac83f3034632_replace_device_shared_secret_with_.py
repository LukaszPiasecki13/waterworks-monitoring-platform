"""replace device shared-secret with asymmetric device_credentials

Revision ID: ac83f3034632
Revises: 4a2eebcdc30a
Create Date: 2026-08-21 19:27:15.195761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac83f3034632'
down_revision: Union[str, Sequence[str], None] = '4a2eebcdc30a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create device_credentials table first
    op.create_table('device_credentials',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('serial_number', sa.String(length=64), nullable=False),
    sa.Column('public_key_pem', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('pending_water_object_id', sa.UUID(), nullable=True),
    sa.Column('pending_challenge', sa.String(length=64), nullable=True),
    sa.Column('challenge_expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('claimed_device_id', sa.UUID(), nullable=True),
    sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('claimed_device_id')
    )
    op.create_index(op.f('ix_device_credentials_serial_number'), 'device_credentials', ['serial_number'], unique=True)

    # Clear existing devices (dev/test data only, no production migration concern)
    op.execute(sa.text("DELETE FROM devices"))

    # Now add the device_credential_id column and drop the old hashed_secret
    op.add_column('devices', sa.Column('device_credential_id', sa.UUID(), nullable=False))
    op.create_index(op.f('ix_devices_device_credential_id'), 'devices', ['device_credential_id'], unique=True)
    op.create_foreign_key('fk_devices_device_credential_id', 'devices', 'device_credentials', ['device_credential_id'], ['id'])
    op.drop_column('devices', 'hashed_secret')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('devices', sa.Column('hashed_secret', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_constraint('fk_devices_device_credential_id', 'devices', type_='foreignkey')
    op.drop_index(op.f('ix_devices_device_credential_id'), table_name='devices')
    op.drop_column('devices', 'device_credential_id')
    op.drop_index(op.f('ix_device_credentials_serial_number'), table_name='device_credentials')
    op.drop_table('device_credentials')
