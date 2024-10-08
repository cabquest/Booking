"""realidgiven

Revision ID: cc7eee13e055
Revises: 472ead6834f5
Create Date: 2024-07-03 10:29:15.303657

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc7eee13e055'
down_revision = '472ead6834f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.add_column(sa.Column('driver_id', sa.Integer(), nullable=False))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('user_id')

    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.drop_column('driver_id')

    # ### end Alembic commands ###
