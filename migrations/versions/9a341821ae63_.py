"""empty message

Revision ID: 9a341821ae63
Revises: fdf8a84ccb4f
Create Date: 2024-07-29 14:37:18.340474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a341821ae63'
down_revision = 'fdf8a84ccb4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_constraint('posts_game_id_fkey', type_='foreignkey')
        batch_op.drop_column('game_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('posts_game_id_fkey', 'games', ['game_id'], ['id'])

    # ### end Alembic commands ###
