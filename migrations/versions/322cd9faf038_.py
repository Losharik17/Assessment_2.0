"""empty message

Revision ID: 322cd9faf038
Revises: 
Create Date: 2021-11-01 11:09:31.490582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '322cd9faf038'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('phone_number', sa.String(length=16), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('expert_id', sa.Integer(), nullable=True),
    sa.Column('viewer_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_admin_email'), 'admin', ['email'], unique=True)
    op.create_table('expert',
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('photo', sa.String(length=1024), nullable=True),
    sa.Column('project_number', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_expert_email'), 'expert', ['email'], unique=False)
    op.create_table('project',
    sa.Column('number', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('start', sa.Date(), nullable=True),
    sa.Column('end', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('number'),
    sa.UniqueConstraint('number')
    )
    op.create_table('user',
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('team', sa.String(length=32), nullable=True),
    sa.Column('region', sa.String(length=64), nullable=True),
    sa.Column('project_number', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('photo', sa.String(length=1024), nullable=True),
    sa.Column('sum_grade_0', sa.Float(), nullable=True),
    sa.Column('sum_grade_1', sa.Float(), nullable=True),
    sa.Column('sum_grade_2', sa.Float(), nullable=True),
    sa.Column('sum_grade_3', sa.Float(), nullable=True),
    sa.Column('sum_grade_4', sa.Float(), nullable=True),
    sa.Column('sum_grade_5', sa.Float(), nullable=True),
    sa.Column('sum_grade_6', sa.Float(), nullable=True),
    sa.Column('sum_grade_7', sa.Float(), nullable=True),
    sa.Column('sum_grade_8', sa.Float(), nullable=True),
    sa.Column('sum_grade_9', sa.Float(), nullable=True),
    sa.Column('sum_grade_all', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=False)
    op.create_table('viewer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('organization', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('phone_number', sa.String(length=16), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('expert_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_viewer_email'), 'viewer', ['email'], unique=True)
    op.create_table('waiting_user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('organization', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('phone_number', sa.String(length=16), nullable=True),
    sa.Column('registration_date', sa.DateTime(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_waiting_user_email'), 'waiting_user', ['email'], unique=True)
    op.create_table('grade',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('expert_id', sa.String(length=64), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('parameter_0', sa.Integer(), nullable=True),
    sa.Column('parameter_1', sa.Integer(), nullable=True),
    sa.Column('parameter_2', sa.Integer(), nullable=True),
    sa.Column('parameter_3', sa.Integer(), nullable=True),
    sa.Column('parameter_4', sa.Integer(), nullable=True),
    sa.Column('parameter_5', sa.Integer(), nullable=True),
    sa.Column('parameter_6', sa.Integer(), nullable=True),
    sa.Column('parameter_7', sa.Integer(), nullable=True),
    sa.Column('parameter_8', sa.Integer(), nullable=True),
    sa.Column('parameter_9', sa.Integer(), nullable=True),
    sa.Column('comment', sa.Text(length=200), nullable=True),
    sa.ForeignKeyConstraint(['expert_id'], ['expert.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('parameter',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('project_number', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_number'], ['project.number'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('viewer_projects',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('viewer_id', sa.Integer(), nullable=True),
    sa.Column('project_number', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_number'], ['project.number'], ),
    sa.ForeignKeyConstraint(['viewer_id'], ['viewer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('viewer_projects')
    op.drop_table('parameter')
    op.drop_table('grade')
    op.drop_index(op.f('ix_waiting_user_email'), table_name='waiting_user')
    op.drop_table('waiting_user')
    op.drop_index(op.f('ix_viewer_email'), table_name='viewer')
    op.drop_table('viewer')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('project')
    op.drop_index(op.f('ix_expert_email'), table_name='expert')
    op.drop_table('expert')
    op.drop_index(op.f('ix_admin_email'), table_name='admin')
    op.drop_table('admin')
    # ### end Alembic commands ###