"""bookingdrivernulltrue

Revision ID: 9c774871f9c0
Revises: c805903b79d3
Create Date: 2024-07-15 17:56:06.972820

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9c774871f9c0'
down_revision = 'c805903b79d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.alter_column('driver_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.alter_column('driver_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
