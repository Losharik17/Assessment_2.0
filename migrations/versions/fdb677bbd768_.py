"""empty message

Revision ID: fdb677bbd768
Revises: 1588bb81011c
Create Date: 2021-08-13 11:08:06.938465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdb677bbd768'
down_revision = '1588bb81011c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('waiting_user', sa.Column('registration_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('waiting_user', 'registration_date')
    # ### end Alembic commands ###
