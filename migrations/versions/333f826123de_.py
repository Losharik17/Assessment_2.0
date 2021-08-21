"""empty message

Revision ID: 333f826123de
Revises: c7d46b0fae29
Create Date: 2021-08-21 18:18:53.153795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '333f826123de'
down_revision = 'c7d46b0fae29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('viewer', sa.Column('expert_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'viewer', ['expert_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'viewer', type_='unique')
    op.drop_column('viewer', 'expert_id')
    # ### end Alembic commands ###