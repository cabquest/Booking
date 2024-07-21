"""jstagain migrate

Revision ID: 5874f67ef9dc
Revises: cc7eee13e055
Create Date: 2024-07-03 11:34:08.255561

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5874f67ef9dc'
down_revision = 'cc7eee13e055'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vehicle', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('base_price', mysql.DECIMAL(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('base_distance_KM', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('price_per_km', mysql.DECIMAL(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('make', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('model', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('license_plate', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.drop_column('license_plate')
        batch_op.drop_column('model')
        batch_op.drop_column('make')
        batch_op.drop_column('price_per_km')
        batch_op.drop_column('base_distance_KM')
        batch_op.drop_column('base_price')
        batch_op.drop_column('vehicle')

    # ### end Alembic commands ###