from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.achievement import ReceivedAchievement

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models.achievement import AchievementORM
    from fanfan.adapters.db.models.user import UserORM


class ReceivedAchievementORM(Base):
    __tablename__ = "received_achievements"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Achievement relation
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"),
    )
    achievement: Mapped[AchievementORM] = relationship(viewonly=True)

    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[UserORM] = relationship(foreign_keys=user_id)

    # From user relation
    from_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    from_user: Mapped[UserORM | None] = relationship(foreign_keys=from_user_id)

    # Constraint
    UniqueConstraint(user_id, achievement_id)

    @classmethod
    def from_model(cls, model: ReceivedAchievement) -> ReceivedAchievementORM:
        return ReceivedAchievementORM(
            id=model.id,
            achievement_id=model.achievement_id,
            user_id=model.user_id,
        )
