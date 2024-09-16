from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.core.models.achievement import AchievementDTO, UserAchievementDTO
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.mixins.order import OrderMixin

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.received_achievement import ReceivedAchievement


class Achievement(Base, OrderMixin):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(nullable=True)
    secret_id: Mapped[str] = mapped_column(unique=True)  # Secret ID for quest

    # Relationships
    user_received: Mapped[ReceivedAchievement | None] = relationship(
        lazy="raise",
        viewonly=True,
    )

    def __str__(self) -> str:
        return self.title

    def to_dto(self) -> AchievementDTO:
        return AchievementDTO(
            id=self.id, title=self.title, description=self.description
        )

    def to_user_dto(self) -> UserAchievementDTO:
        return UserAchievementDTO(
            id=self.id,
            title=self.title,
            description=self.description,
            received=bool(self.user_received),
        )
