"""bookingdetailsadded

Revision ID: cd25285149f6
Revises: fdbc20444305
Create Date: 2024-07-16 00:05:45.701306

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cd25285149f6'
down_revision = 'fdbc20444305'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=30),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.String(length=30),
               type_=mysql.VARCHAR(length=20),
               existing_nullable=False)

    # ### end Alembic commands ###
