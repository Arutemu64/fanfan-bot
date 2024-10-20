from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.event import EventId
from fanfan.core.models.subscription import (
    FullSubscriptionModel,
    SubscriptionId,
    SubscriptionModel,
)
from fanfan.core.models.user import UserId

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import Event, User


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    counter: Mapped[int] = mapped_column(server_default="5")

    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship()

    # Event relation
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    event: Mapped[Event] = relationship()
    UniqueConstraint(event_id, user_id)

    def to_model(self) -> SubscriptionModel:
        return SubscriptionModel(
            id=SubscriptionId(self.id),
            user_id=UserId(self.user_id),
            event_id=EventId(self.event_id),
            counter=self.counter,
        )

    def to_full_model(self) -> FullSubscriptionModel:
        return FullSubscriptionModel(
            id=SubscriptionId(self.id),
            user_id=UserId(self.user_id),
            event_id=EventId(self.event_id),
            counter=self.counter,
            event=self.event.to_full_model() if self.event else None,
        )
