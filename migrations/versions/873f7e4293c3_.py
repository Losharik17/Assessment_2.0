"""empty message

Revision ID: 873f7e4293c3
Revises: 
Create Date: 2021-10-14 14:37:03.657597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '873f7e4293c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('photo', sa.String(length=1024), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'photo')
    # ### end Alembic commands ###