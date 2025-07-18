"""Add promotion_services association table for Promotion-Service many-to-many

Revision ID: 0c3dbbf7057b
Revises: a03d1248ae33
Create Date: 2025-07-01 11:20:27.674812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c3dbbf7057b'
down_revision = 'a03d1248ae33'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promotion_services',
    sa.Column('promotion_id', sa.String(length=36), nullable=False),
    sa.Column('service_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('promotion_id', 'service_id')
    )
    op.drop_constraint('rotations_planning_id_fkey', 'rotations', type_='foreignkey')
    op.create_foreign_key(None, 'rotations', 'plannings', ['planning_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rotations', type_='foreignkey')
    op.create_foreign_key('rotations_planning_id_fkey', 'rotations', 'plannings', ['planning_id'], ['id'], ondelete='CASCADE')
    op.drop_table('promotion_services')
    # ### end Alembic commands ### 