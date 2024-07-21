"""second migrate

Revision ID: 472ead6834f5
Revises: f6eb37177918
Create Date: 2024-07-02 13:50:34.762889

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '472ead6834f5'
down_revision = 'f6eb37177918'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.drop_column('is_verified')
        batch_op.drop_column('location')
        batch_op.drop_column('status')
        batch_op.drop_column('KYC_verified')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('location')
        batch_op.drop_column('is_blocked')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_blocked', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('location', mysql.VARCHAR(length=150), nullable=True))

    with op.batch_alter_table('driver', schema=None) as batch_op:
        batch_op.add_column(sa.Column('KYC_verified', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('status', mysql.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('location', mysql.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('is_verified', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))

    # ### end Alembic commands ###