"""nominations_change

Revision ID: 019
Revises: 018
Create Date: 2024-10-20 16:36:13.539414

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # BREAKING MIGRATION - Nomination ID type changes from varchar to integer
    # You should handle this manually (backup, delete nominations, migrate, restore)
    # Create code column
    op.add_column("nominations", sa.Column("code", sa.String(), nullable=False))
    op.create_unique_constraint(op.f("uq_nominations_code"), "nominations", ["code"])
    # Remove fk constraint
    op.execute(
        "ALTER TABLE participants "
        "DROP CONSTRAINT fk_participants_nomination_id_nominations"
    )
    # Change type
    op.execute(
        "ALTER TABLE nominations ALTER COLUMN id TYPE integer USING (id::integer)"
    )
    op.execute(
        "ALTER TABLE participants "
        "ALTER COLUMN nomination_id TYPE integer USING (nomination_id::integer)"
    )
    # Add sequence for nomination id
    op.execute(
        "CREATE SEQUENCE nominations_id_seq "
        "AS integer START 1 "
        "OWNED BY nominations.id"
    )
    op.execute(
        "ALTER TABLE nominations "
        "ALTER COLUMN id "
        "SET DEFAULT nextval('nominations_id_seq')"
    )
    # Restore fk constraint
    op.create_foreign_key(
        op.f("fk_participants_nomination_id_nominations"),
        "participants",
        "nominations",
        ["nomination_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop code column
    op.drop_constraint(op.f("uq_nominations_code"), "nominations", type_="unique")
    op.drop_column("nominations", "code")
    # Remove fk constraint
    op.execute(
        "ALTER TABLE participants "
        "DROP CONSTRAINT fk_participants_nomination_id_nominations"
    )
    # Change type back
    op.execute("ALTER TABLE nominations ALTER COLUMN id TYPE varchar")
    op.execute("ALTER TABLE participants ALTER COLUMN nomination_id TYPE varchar")
    # Remove nomination id sequence
    op.execute("ALTER TABLE nominations " "ALTER COLUMN id " "SET DEFAULT NULL")
    op.execute("DROP SEQUENCE nominations_id_seq")
    # Restore fk constraint
    op.create_foreign_key(
        op.f("fk_participants_nomination_id_nominations"),
        "participants",
        "nominations",
        ["nomination_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###