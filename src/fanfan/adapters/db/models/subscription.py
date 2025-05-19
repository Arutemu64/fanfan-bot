from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.subscription import Subscription
from fanfan.core.vo.schedule_event import ScheduleEventId
from fanfan.core.vo.subscription import SubscriptionId
from fanfan.core.vo.user import UserId

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import ScheduleEventORM, UserORM


class SubscriptionORM(Base):
    __tablename__ = "subscriptions"

    id: Mapped[SubscriptionId] = mapped_column(primary_key=True)
    counter: Mapped[int] = mapped_column()

    # User relation
    user_id: Mapped[UserId] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[UserORM] = relationship()

    # Event relation
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    event: Mapped[ScheduleEventORM] = relationship()

    # Constraint
    UniqueConstraint(event_id, user_id)

    @classmethod
    def from_model(cls, model: Subscription):
        return SubscriptionORM(
            id=model.id,
            user_id=model.user_id,
            event_id=model.event_id,
            counter=model.counter,
        )

    def to_model(self) -> Subscription:
        return Subscription(
            id=SubscriptionId(self.id),
            user_id=UserId(self.user_id),
            event_id=ScheduleEventId(self.event_id),
            counter=self.counter,
        )
