from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.achievement import ReceivedAchievementDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models.achievement import Achievement
    from fanfan.infrastructure.db.models.user import User


class ReceivedAchievement(Base):
    __tablename__ = "received_achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"),
    )

    UniqueConstraint(user_id, achievement_id)

    user: Mapped[User] = relationship(viewonly=True)
    achievement: Mapped[Achievement] = relationship(viewonly=True)

    def to_dto(self) -> ReceivedAchievementDTO:
        return ReceivedAchievementDTO(
            user_id=self.user_id,
            achievement_id=self.achievement_id,
        )
