"""location added

Revision ID: f6de6a05f74e
Revises: 5874f67ef9dc
Create Date: 2024-07-04 09:28:44.948985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6de6a05f74e'
down_revision = '5874f67ef9dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.add_column(sa.Column('latitude', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('longitude', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.drop_column('status')
        batch_op.drop_column('longitude')
        batch_op.drop_column('latitude')

    # ### end Alembic commands ###