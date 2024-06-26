from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UUID, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.achievement import AchievementDTO, FullAchievementDTO
from fanfan.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.received_achievement import ReceivedAchievement


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order: Mapped[float] = mapped_column(
        unique=True,
        nullable=False,
        server_default=Sequence("achievements_order_seq", start=1).next_value(),
    )
    secret_id: Mapped[UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        nullable=True,
        unique=True,
    )
    title: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    user_received: Mapped[Optional[ReceivedAchievement]] = relationship(
        lazy="raise",
        viewonly=True,
    )

    def to_dto(self) -> AchievementDTO:
        return AchievementDTO.model_validate(self)

    def to_full_dto(self) -> FullAchievementDTO:
        return FullAchievementDTO.model_validate(self)

    def __str__(self):
        return self.title
