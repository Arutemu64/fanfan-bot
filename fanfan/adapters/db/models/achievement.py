from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.achievement import (
    Achievement,
    AchievementId,
    FullAchievement,
)

if TYPE_CHECKING:
    from fanfan.adapters.db.models.received_achievement import DBReceivedAchievement


class DBAchievement(Base, OrderMixin):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    # Secret ID for quest
    secret_id: Mapped[str] = mapped_column(unique=True)

    # Relationships
    user_received: Mapped[DBReceivedAchievement | None] = relationship(
        lazy="raise",
        viewonly=True,
    )

    def __str__(self) -> str:
        return self.title

    def to_model(self) -> Achievement:
        return Achievement(
            id=AchievementId(self.id), title=self.title, description=self.description
        )

    def to_full_model(self) -> FullAchievement:
        return FullAchievement(
            id=AchievementId(self.id),
            title=self.title,
            description=self.description,
            received=bool(self.user_received),
        )
