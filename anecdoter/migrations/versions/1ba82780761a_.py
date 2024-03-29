"""empty message

Revision ID: 1ba82780761a
Revises: d29f5934786d
Create Date: 2022-12-17 13:09:48.162001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ba82780761a'
down_revision = 'd29f5934786d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rated_jokes', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'rated_jokes', 'users', ['user_id'], ['user_id'])
    op.drop_column('rated_jokes', 'word')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rated_jokes', sa.Column('word', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'rated_jokes', type_='foreignkey')
    op.drop_column('rated_jokes', 'user_id')
    # ### end Alembic commands ###
