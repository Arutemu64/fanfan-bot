from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.subscription import SubscriptionDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models import Event


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    counter: Mapped[int] = mapped_column(server_default="5")

    UniqueConstraint(event_id, user_id)

    event: Mapped[Event] = relationship()

    def to_dto(self) -> SubscriptionDTO:
        return SubscriptionDTO(
            id=self.id,
            event_id=self.event_id,
            user_id=self.user_id,
            counter=self.counter,
            event=self.event.to_dto(),
        )
