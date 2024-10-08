"""unnullable.

Revision ID: 002
Revises: 001
Create Date: 2024-03-11 21:14:06.323381

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("schedule", "title", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        "schedule",
        "skip",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text("false"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "schedule",
        "skip",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=sa.text("false"),
    )
    op.alter_column("schedule", "title", existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###
