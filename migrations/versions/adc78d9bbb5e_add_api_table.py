"""add api table.

Revision ID: adc78d9bbb5e
Revises: 666db36826f4
Create Date: 2022-09-24 21:53:21.772721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adc78d9bbb5e'
down_revision = '666db36826f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('server_api',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('server', sa.String(length=50), nullable=True),
    sa.Column('url', sa.String(length=200), nullable=True),
    sa.Column('method', sa.String(length=50), nullable=True),
    sa.Column('monitor', sa.Boolean(), nullable=True),
    sa.Column('latest_code', sa.Integer(), nullable=True),
    sa.Column('aver_res_time', sa.Float(), nullable=True),
    sa.Column('aver_err_rate', sa.Float(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('server_api')
    # ### end Alembic commands ###