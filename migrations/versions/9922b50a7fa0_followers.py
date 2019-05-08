"""followers

Revision ID: 9922b50a7fa0
Revises: fac108b1f43f
Create Date: 2019-05-05 15:16:26.276064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9922b50a7fa0'
down_revision = 'fac108b1f43f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
