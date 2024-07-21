"""distanceaddedtobooking

Revision ID: 84471575a4d0
Revises: 0b6908dcf800
Create Date: 2024-07-14 14:09:36.199183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84471575a4d0'
down_revision = '0b6908dcf800'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('distance', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_column('distance')

    # ### end Alembic commands ###