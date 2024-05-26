from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.subscription import FullSubscriptionDTO, SubscriptionDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models import Event


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    counter: Mapped[int] = mapped_column(server_default="5")

    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Event relation
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    event: Mapped[Event] = relationship()
    UniqueConstraint(event_id, user_id)

    def to_dto(self) -> SubscriptionDTO:
        return SubscriptionDTO.model_validate(self)

    def to_full_dto(self) -> FullSubscriptionDTO:
        return FullSubscriptionDTO.model_validate(self)
