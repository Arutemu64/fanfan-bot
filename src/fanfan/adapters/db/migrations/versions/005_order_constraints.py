"""order_constraints

Revision ID: 005
Revises: 004
Create Date: 2024-12-25 18:29:59.458283

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE schedule DROP CONSTRAINT uq_schedule_order")
    op.execute(
        """ALTER TABLE schedule ADD CONSTRAINT uq_schedule_order UNIQUE ("order") DEFERRABLE INITIALLY DEFERRED"""  # noqa: E501
    )
    op.execute("ALTER TABLE achievements DROP CONSTRAINT uq_achievements_order")
    op.execute(
        """ALTER TABLE achievements ADD CONSTRAINT uq_achievements_order UNIQUE ("order") DEFERRABLE INITIALLY DEFERRED"""  # noqa: E501
    )
    op.execute("ALTER TABLE activities DROP CONSTRAINT uq_activities_order")
    op.execute(
        """ALTER TABLE activities ADD CONSTRAINT uq_activities_order UNIQUE ("order") DEFERRABLE INITIALLY DEFERRED"""  # noqa: E501
    )
    op.execute("ALTER TABLE participants DROP CONSTRAINT uq_participants_nomination_id")
    op.execute(
        """ALTER TABLE participants ADD CONSTRAINT uq_participants_nomination_id UNIQUE (nomination_id, voting_number) DEFERRABLE INITIALLY DEFERRED"""  # noqa: E501
    )


def downgrade() -> None:
    op.execute("ALTER TABLE schedule DROP CONSTRAINT uq_schedule_order")
    op.execute(
        """ALTER TABLE schedule ADD CONSTRAINT uq_schedule_order UNIQUE ("order") NOT DEFERRABLE"""  # noqa: E501
    )
    op.execute("ALTER TABLE achievements DROP CONSTRAINT uq_achievements_order")
    op.execute(
        """ALTER TABLE achievements ADD CONSTRAINT uq_achievements_order UNIQUE ("order") NOT DEFERRABLE"""  # noqa: E501
    )
    op.execute("ALTER TABLE activities DROP CONSTRAINT uq_activities_order")
    op.execute(
        """ALTER TABLE activities ADD CONSTRAINT uq_activities_order UNIQUE ("order") NOT DEFERRABLE"""  # noqa: E501
    )
    op.execute("ALTER TABLE participants DROP CONSTRAINT uq_participants_nomination_id")
    op.execute(
        """ALTER TABLE participants ADD CONSTRAINT uq_participants_nomination_id UNIQUE (nomination_id, voting_number) NOT DEFERRABLE"""  # noqa: E501
    )
