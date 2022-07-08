"""add a column in card table

Revision ID: cc330a7b098e
Revises: c9441f88d503
Create Date: 2022-07-08 22:15:37.771760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc330a7b098e'
down_revision = 'c9441f88d503'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cardRelatedCard',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('case', sa.Integer(), nullable=True),
    sa.Column('card', sa.Integer(), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['card'], ['card.id'], ),
    sa.ForeignKeyConstraint(['case'], ['case.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('card', sa.Column('original_link', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('card', 'original_link')
    op.drop_table('cardRelatedCard')
    # ### end Alembic commands ###