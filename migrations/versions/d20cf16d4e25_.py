"""empty message

Revision ID: d20cf16d4e25
Revises: 2b57da4e29c3
Create Date: 2024-08-19 13:14:29.509463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd20cf16d4e25'
down_revision = '2b57da4e29c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee_service', schema=None) as batch_op:
        batch_op.alter_column('employee_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('service_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee_service', schema=None) as batch_op:
        batch_op.alter_column('service_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('employee_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###
