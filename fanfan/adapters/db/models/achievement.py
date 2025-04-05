from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.achievement import (
    Achievement,
    AchievementFull,
    AchievementId,
)

if TYPE_CHECKING:
    from fanfan.adapters.db.models.received_achievement import ReceivedAchievementORM


class AchievementORM(Base, OrderMixin):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    # Secret ID for quest
    secret_id: Mapped[str] = mapped_column(unique=True)

    # Relationships
    user_received: Mapped[ReceivedAchievementORM | None] = relationship(
        lazy="raise",
        viewonly=True,
    )

    def __str__(self) -> str:
        return self.title

    def to_model(self) -> Achievement:
        return Achievement(
            id=AchievementId(self.id), title=self.title, description=self.description
        )

    def to_full_model(self) -> AchievementFull:
        return AchievementFull(
            id=AchievementId(self.id),
            title=self.title,
            description=self.description,
            received=bool(self.user_received),
        )
