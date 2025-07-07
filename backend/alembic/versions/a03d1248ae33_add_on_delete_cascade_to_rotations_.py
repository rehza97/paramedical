"""Add ON DELETE CASCADE to rotations.planning_id

Revision ID: a03d1248ae33
Revises: 
Create Date: 2025-07-01 01:43:47.903024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a03d1248ae33'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old foreign key constraint
    op.drop_constraint('rotations_planning_id_fkey',
                       'rotations', type_='foreignkey')
    # Add a new one with ON DELETE CASCADE
    op.create_foreign_key(
        'rotations_planning_id_fkey',
        'rotations', 'plannings',
        ['planning_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('rotations_planning_id_fkey',
                       'rotations', type_='foreignkey')
    op.create_foreign_key(
        'rotations_planning_id_fkey',
        'rotations', 'plannings',
        ['planning_id'], ['id']
        # No cascade on downgrade
    )
