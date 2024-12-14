from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.event import EventId
from fanfan.core.models.subscription import (
    FullSubscription,
    Subscription,
    SubscriptionId,
)
from fanfan.core.models.user import UserId

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import DBEvent, DBUser


class DBSubscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    counter: Mapped[int] = mapped_column()

    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[DBUser] = relationship()

    # Event relation
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    event: Mapped[DBEvent] = relationship()

    # Constraint
    UniqueConstraint(event_id, user_id)

    @classmethod
    def from_model(cls, model: Subscription):
        return DBSubscription(
            id=model.id,
            user_id=model.user_id,
            event_id=model.event_id,
            counter=model.counter,
        )

    def to_model(self) -> Subscription:
        return Subscription(
            id=SubscriptionId(self.id),
            user_id=UserId(self.user_id),
            event_id=EventId(self.event_id),
            counter=self.counter,
        )

    def to_full_model(self) -> FullSubscription:
        return FullSubscription(
            id=SubscriptionId(self.id),
            user_id=UserId(self.user_id),
            event_id=EventId(self.event_id),
            counter=self.counter,
            event=self.event.to_full_model() if self.event else None,
        )
