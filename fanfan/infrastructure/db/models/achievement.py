from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.achievement import AchievementDTO, FullAchievementDTO
from fanfan.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.received_achievement import ReceivedAchievement


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    user_received: Mapped[Optional[ReceivedAchievement]] = relationship(
        lazy="raise", viewonly=True
    )

    def to_dto(self) -> AchievementDTO:
        return AchievementDTO(
            id=self.id, title=self.title, description=self.description
        )

    def to_full_dto(self) -> FullAchievementDTO:
        return FullAchievementDTO(
            id=self.id,
            title=self.title,
            description=self.description,
            user_received=self.user_received.to_dto() if self.user_received else None,
        )

    def __str__(self):
        return self.title
