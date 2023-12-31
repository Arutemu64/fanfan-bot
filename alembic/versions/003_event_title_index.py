"""event_title_index

Revision ID: 003
Revises: 002
Create Date: 2023-10-22 15:24:30.676386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_schedule_title'), 'schedule', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_schedule_title'), table_name='schedule')
    # ### end Alembic commands ###
