from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.achievement import (
    Achievement,
)
from fanfan.core.vo.achievements import AchievementId


class AchievementORM(Base, OrderMixin):
    __tablename__ = "achievements"

    id: Mapped[AchievementId] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column()

    def __str__(self) -> str:
        return self.title

    def to_model(self) -> Achievement:
        return Achievement(id=self.id, title=self.title, description=self.description)
