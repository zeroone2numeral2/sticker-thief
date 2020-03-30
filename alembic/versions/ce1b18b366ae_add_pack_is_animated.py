"""add pack_is_animated

Revision ID: ce1b18b366ae
Revises: 
Create Date: 2020-03-31 00:10:31.844047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce1b18b366ae'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('packs', sa.Column('is_animated', sa.Boolean, default=False))


def downgrade():
    pass
