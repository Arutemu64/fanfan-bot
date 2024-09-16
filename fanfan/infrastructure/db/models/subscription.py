from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.core.models.subscription import FullSubscriptionDTO, SubscriptionDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models import Event, User


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

    def to_dto(self) -> SubscriptionDTO:
        return SubscriptionDTO(
            id=self.id,
            user_id=self.user_id,
            event_id=self.event_id,
            counter=self.counter,
        )

    def to_full_dto(self) -> FullSubscriptionDTO:
        self.event: Event
        return FullSubscriptionDTO(
            id=self.id,
            user_id=self.user_id,
            event_id=self.event_id,
            counter=self.counter,
            event=self.event.to_dto() if self.event else None,
        )
