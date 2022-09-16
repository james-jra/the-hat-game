"""empty message

Revision ID: f9a0806da390
Revises: 1ca6c9ea0f76
Create Date: 2020-05-30 20:01:17.301044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9a0806da390'
down_revision = '1ca6c9ea0f76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game', sa.Column('n_picks', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'n_picks')
    # ### end Alembic commands ###