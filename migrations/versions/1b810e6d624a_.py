"""empty message

Revision ID: 1b810e6d624a
Revises: 794337257346
Create Date: 2022-08-25 11:57:53.796486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b810e6d624a'
down_revision = '794337257346'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rated_jokes', sa.Column('joke', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rated_jokes', 'joke')
    # ### end Alembic commands ###
