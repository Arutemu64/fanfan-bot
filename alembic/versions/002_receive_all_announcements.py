"""receive_all_announcements

Revision ID: 002
Revises: 001
Create Date: 2023-08-13 08:45:48.782215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'nominations', ['id'])
    op.create_unique_constraint(None, 'participants', ['id'])
    op.create_unique_constraint(None, 'schedule', ['id'])
    op.create_unique_constraint(None, 'subscriptions', ['id'])
    op.create_unique_constraint(None, 'tickets', ['id'])
    op.add_column('users', sa.Column('receive_all_announcements', sa.Boolean(), server_default='False', nullable=False))
    op.create_unique_constraint(None, 'users', ['id'])
    op.create_unique_constraint(None, 'votes', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'votes', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'receive_all_announcements')
    op.drop_constraint(None, 'tickets', type_='unique')
    op.drop_constraint(None, 'subscriptions', type_='unique')
    op.drop_constraint(None, 'schedule', type_='unique')
    op.drop_constraint(None, 'participants', type_='unique')
    op.drop_constraint(None, 'nominations', type_='unique')
    # ### end Alembic commands ###