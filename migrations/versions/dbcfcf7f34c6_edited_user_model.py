"""edited user model

Revision ID: dbcfcf7f34c6
Revises: 5bc68f800132
Create Date: 2019-05-12 14:45:15.630454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbcfcf7f34c6'
down_revision = '5bc68f800132'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('movie_vote1', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('movie_vote2', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('movie_vote3', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('movie_vote4', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('movie_vote5', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('voted', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'voted')
    op.drop_column('user', 'movie_vote5')
    op.drop_column('user', 'movie_vote4')
    op.drop_column('user', 'movie_vote3')
    op.drop_column('user', 'movie_vote2')
    op.drop_column('user', 'movie_vote1')
    # ### end Alembic commands ###
